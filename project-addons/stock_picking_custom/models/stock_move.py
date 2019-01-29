# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'


    @api.multi
    def _get_product_default_location_id(self):
        for move in self:
            move.default_product_dest_location_id = move.location_dest_id.get_putaway_strategy(move.product_id).id
            move.default_product_location_id = move.location_id.get_putaway_strategy(move.product_id).id


    default_product_location_id = fields.Many2one('stock.location', compute="_get_product_default_location_id",
                                                  string="Default location")
    default_product_dest_location_id = fields.Many2one('stock.location', compute="_get_product_default_location_id",
                                                       string="Default destination location")
