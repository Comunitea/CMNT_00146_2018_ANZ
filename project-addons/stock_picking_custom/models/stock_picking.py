# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields
from odoo.addons import decimal_precision as dp

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
    reserved_availability = fields.Float(
        'Quantity Reserved', compute='compute_picking_qties',
        digits=dp.get_precision('Product Unit of Measure'))
    quantity_done = fields.Float(
        'Quantity Done', compute='compute_picking_qties',
        digits=dp.get_precision('Product Unit of Measure'))
    product_uom_qty = fields.Float(
        'Quantity', compute='compute_picking_qties',
        digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    def compute_picking_qties(self):
        for pick in self:
            pick.quantity_done = sum(x.quantity_done for x in pick.move_lines)
            pick.reserved_availability = sum(x.reserved_availability for x in pick.move_lines)
            pick.product_uom_qty = sum(x.product_uom_qty for x in pick.move_lines)


    @api.multi
    def force_set_qty_done(self):
        model = self._context.get('model_dest','stock.move')
        for picking in self:
            if model == 'move.line':
                picking.move_lines.force_set_qty_done()
            else:
                picking.move_line_ids.force_set_qty_done()


    @api.multi
    def force_set_assigned_qty_done(self):
        model = self._context.get('model_dest','stock.move')
        for picking in self:
            if model == 'move.line':
                picking.move_lines.force_set_assigned_qty_done()
            else:
                picking.move_line_ids.force_set_assigned_qty_done()

    @api.multi
    def force_reset_qties(self):
        model = self._context.get('model_dest', 'stock.move')
        for picking in self:
            picking.move_line_ids.filtered(lambda x: x.state != 'done').write({'qty_done': 0})
            continue
            if model == 'move.line':
                picking.move_lines.filtered(lambda x: x.state != 'done').write({'qty_done': 0})
            else:
                picking.move_line_ids.write({'qty_done': 0})

    @api.multi
    def force_set_available_qty_done(self):
        model = self._context.get('model_dest','stock.move')
        for picking in self:
            if model == 'move.line':
                picking.move_lines.force_set_available_qty_done()
            else:
                picking.move_line_ids.force_set_available_qty_done()

    @api.multi
    def action_done(self):
        return super().action_done()
        moves = self.filtered(lambda x: x.company_id.id == 3).mapped('move_lines').filtered(lambda x: x.state == 'done')
        if moves:
            self.env['procurement.group'].run_procurement_for_stock_move(moves,False, moves[0].company_id.id)
        return res


    @api.multi
    def action_assign_batch(self):
        domain = [('picking_id.picking_type_code', '=', 'outgoing'), ('state', 'in', ('confirmed', 'partially_available'))]
        self.env['stock.move'].search(domain)._action_assign()

