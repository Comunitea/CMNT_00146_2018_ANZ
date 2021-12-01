# Copyright 2021 Comunitea - Kiko Sánchez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductStockAvailableMixin(models.AbstractModel):
    _inherit = 'product.stock.available.mixin'

    
    def _search_qty_available_global(self, operator, value):
        name = 'qty_available'
        return self.sudo()._search_product_quantity(operator, value, name)
    
    def _search_incoming_qty_global(self, operator, value):
        name = 'incoming_qty'
        return self.sudo()._search_product_quantity(operator, value, name)
    
    def _search_outgoing_qty_global(self, operator, value):
        name = 'outgoing_qty'
        return self.sudo()._search_product_quantity(operator, value, name)

    def _search_virtual_available_global(self, operator, value):
        name = 'virtual_available'
        return self.sudo()._search_product_quantity(operator, value, name)