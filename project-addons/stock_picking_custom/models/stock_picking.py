# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


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

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    order_field = fields.Selection([
        ('location_id', 'Ubicación de origen'), 
        ('location_dest_id', 'Ubicación de destino'), 
        ('package_id', 'Paquete de origen'), 
        ('result_package_id', 'Paquete de destino')], 'Campo de orden en movimeintos')
    
    def get_move_order_field(self):
        if self.order_field in ('location_id', 'location_dest_id'):
            return {'model': 'stock.location',
                    'order_field': self.order_field,
                    'field': 'sequence'}

        if self.order_field in ('package_id', 'result_package_id'):
            return {'model': 'stock.quant.package',
                    'order_field': self.order_field,
                    'field': 'name'}

        return {'model': 'stock.location',
                'order_field': 'location_id',
                'field': 'sequence'}

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
    reserved_availability_lines = fields.Float(
        'Quantity Reserved', compute='compute_picking_qties',
        digits=dp.get_precision('Product Unit of Measure'))
    quantity_done_lines = fields.Float(
        'Quantity Done', compute='compute_picking_qties',
        digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    def compute_picking_qties(self):
        for pick in self:
            pick.quantity_done = sum(x.quantity_done for x in pick.move_lines)
            pick.reserved_availability = sum(x.reserved_availability for x in pick.move_lines)
            pick.quantity_done_lines = sum(x.qty_done for x in pick.move_line_ids)
            pick.reserved_availability_lines = sum(x.product_uom_qty for x in pick.move_line_ids)


    @api.multi
    def force_set_qty_done(self):
        model = self._context.get('model_dest', 'stock.move')
        for picking in self:
            if model == 'move.line':
                picking.move_lines.force_set_qty_done()
            else:
                picking.move_line_ids.force_set_qty_done()


    @api.multi
    def force_set_assigned_qty_done(self):
        model = self._context.get('model_dest', 'stock.move')
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

    @api.multi
    def force_set_available_qty_done(self):
        model = self._context.get('model_dest', 'stock.move')
        for picking in self:
            if model == 'move.line':
                picking.move_lines.force_set_available_qty_done()
            else:
                picking.move_line_ids.force_set_available_qty_done()

    @api.multi
    def action_done(self):

        #if any(x.location_dest_id.name == 'Stock' for x in self.move_line_ids):
        #    raise UserError ("No puedes colocar mercancía en stock")

        return super().action_done()

    @api.multi
    def action_assign_batch(self):
        domain = [('picking_id.picking_type_code', '=', 'outgoing'), ('state', 'in', ('confirmed', 'partially_available'))]
        self.env['stock.move'].search(domain)._action_assign()

    @api.multi
    def picking_force_set_qty_done(self):
        ctx = self._context.copy()
        for picking in self:
            picking.move_lines.with_context(ctx).force_set_qty_done()

    @api.multi
    def picking_force_set_assigned_qty_done(self):
        ctx = self._context.copy()
        for picking in self:
            picking.move_lines.with_context(ctx).force_set_assigned_qty_done()

    #APK integration
    @api.model
    def action_assign_pick(self, vals):
        picking = self.browse(vals.get('id', False))
        if not picking:
            return {'err': True, 'error': "No se ha encontrado el albarán"}
        
        res = picking.action_assign()        
        return res

    @api.model
    def button_validate_pick(self, vals):
        picking_id = self.browse(vals.get('id', False))
        if not picking_id:
            return {'err': True, 'error': "No se ha encontrado el albarán"}

        ctx = picking_id._context.copy()
        ctx.update(skip_overprocessed_check=True)
        res = picking_id.with_context(ctx).button_validate()
        if res:
            if res['res_model'] == 'stock.immediate.transfer':
                wiz =  self.env['stock.immediate.transfer'].with_context(res['context']).browse(res['res_id'])
                res_inm = wiz.process()

                if res_inm['res_model'] == 'stock.backorder.confirmation':
                    wiz = self.env['stock.backorder.confirmation'].with_context(res_inm['context']).browse(res_inm['res_id'])
                    res_bord = wiz._process()

            if res['res_model'] == 'stock.backorder.confirmation':
                    wiz = self.env['stock.backorder.confirmation'].with_context(res['context']).browse(res['res_id'])
                    res_boc = wiz._process()
        return {'err': False, 'values': {'id': picking_id.id, 'state': picking_id.state}}

    @api.model
    def force_set_assigned_qty_done_apk(self, vals):
        picking = self.browse(vals.get('id', False))
        if not picking:
            return {'err': True, 'error': "No se ha encontrado el albarán."}
        picking.force_set_assigned_qty_done()        
        return True

    @api.model
    def force_reset_qties_apk(self, vals):
        picking = self.browse(vals.get('id', False))
        if not picking:
            return {'err': True, 'error': "No se ha encontrado el albarán."}
        picking.force_reset_qties()        
        return True