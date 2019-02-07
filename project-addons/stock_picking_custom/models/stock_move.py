# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'


    @api.multi
    def _get_product_default_location_id(self):
        reserved_moves = self.filtered(lambda x: x.move_line_ids)
        print (reserved_moves)
        for move in reserved_moves:
            move.default_product_dest_location_id = move.move_line_ids[0].location_dest_id
            move.default_product_location_id = move.move_line_ids[0].location_id

        for move in (self - reserved_moves):
            domain = [('putaway_id', '=', 1), ('product_product_id', '=', move.product_id.id)]
            spps = self.env['stock.product.putaway.strategy'].search(domain, limit=1)
            move.default_product_dest_location_id = spps.fixed_location_id or move.location_dest_id
            move.default_product_location_id = spps.fixed_location_id or move.location_id


    default_product_location_id = fields.Many2one('stock.location', compute="_get_product_default_location_id",
                                                  string="Default location")
    default_product_dest_location_id = fields.Many2one('stock.location', compute="_get_product_default_location_id",
                                                       string="Default destination location")

    qty_available = fields.Float('Qty available', compute="get_qty_available")

    @api.depends('product_id', 'picking_id.location_id')
    @api.multi
    def get_qty_available(self):
        for line in self:
            line.qty_available = line.product_id.with_context(location=line.picking_id.location_id.id).qty_available

    @api.multi
    def force_set_qty_done(self):
        for move in self.filtered(lambda x: not x.quantity_done):
            move.quantity_done = move.product_uom_qty

    @api.multi
    def force_set_assigned_qty_done(self):
        for move in self.filtered(lambda x: x.reserved_availability and not x.quantity_done):
            move.quantity_done = move.reserved_availability

    @api.multi
    def force_set_available_qty_done(self):
        for move in self.filtered(lambda x: x.qty_available and not x.quantity_done):
            move.quantity_done = move.qty_available



    @api.depends('state', 'picking_id')
    def _compute_is_initial_demand_editable(self):
        for move in self:
            move.is_initial_demand_editable = move.picking_id.is_locked and move.state != 'done'


