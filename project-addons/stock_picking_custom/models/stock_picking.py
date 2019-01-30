# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    to_refund = fields.Boolean(default=True)


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        for line in res.get('product_return_moves', []):
            line[2]['to_refund'] = True
        return res




class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def action_draft(self):
        self.mapped('move_lines')._action_cancel()
        self.write({'is_locked': True})
        return True

    @api.multi
    def action_re_confirm(self):
        self.ensure_one()
        self.mapped('move_lines').filtered(lambda x:x.state == 'cancel').write({'state': 'draft'})
        if all(x.state=='draft' for x in self.move_lines):
            self.action_confirm()

    @api.multi
    def get_domain(self):
        my_categ= self.env.ref('stock_picking_custom.res_partner_delivery_carrier')
        if my_categ:
            domain = [('id', 'in', my_categ.partner_ids.ids)]
        else:
            domain = []
        return domain

    delivery_note = fields.Text('Delivery note')
    carrier_partner_id = fields.Many2one('res.partner', string="Carrier partner", domain=lambda self: self.get_domain())

    @api.multi
    def force_set_qty_done(self):
        for picking in self:
            picking.move_lines.force_set_qty_done()

    @api.multi
    def force_set_assigned_qty_done(self):
        for picking in self:
            picking.move_lines.force_set_assigned_qty_done()

    @api.multi
    def force_reset_qties(self):
        for picking in self:
            picking.move_lines.mapped('move_line_ids').write({'qty_done': 0})

