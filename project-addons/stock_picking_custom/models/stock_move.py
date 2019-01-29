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
