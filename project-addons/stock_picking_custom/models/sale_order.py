# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)], ondelete='restrict')

    def apply_route_id(self):
        self.order_line.write({'route_id': self.route_id})


