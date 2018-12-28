# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def get_sale_order_by_context(self):
        sale_order_by_context =  self._context.get('sale_order_id', False) and self.browse(self._context['sale_order_id']) or self._context.get('order_id', False) and self.browse(self._context['order_id'])
        return sale_order_by_context

    def add_args_to_product_search(self, args):
        return args
