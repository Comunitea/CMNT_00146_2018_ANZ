# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.addons.stock.models.product import OPERATORS


class ProductTemplate(models.Model):
    _inherit = "product.template"

    global_qty_available = fields.Float(
        'Quantity On Hand', compute='_compute_quantities', search='_search_qty_available',
        digits=dp.get_precision('Product Unit of Measure'),
        compute_sudo=True)
    global_virtual_available = fields.Float(
        'Forecast Quantity', compute='_compute_quantities', search='_search_virtual_available',
        digits=dp.get_precision('Product Unit of Measure'),
        compute_sudo=True)
    global_incoming_qty = fields.Float(
        'Incoming', compute='_compute_quantities', search='_search_incoming_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        compute_sudo=True)
    global_outgoing_qty = fields.Float(
        'Outgoing', compute='_compute_quantities', search='_search_outgoing_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        compute_sudo=True)

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_quantities(self):
        res = self.compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'),
                                           self._context.get('package_id'), self._context.get('from_date'),
                                           self._context.get('to_date'))
        for template in self:
            template.global_qty_available = res[template.id]['qty_available']
            template.global_incoming_qty = res[template.id]['incoming_qty']
            template.global_outgoing_qty = res[template.id]['outgoing_qty']
            template.global_virtual_available = res[template.id]['virtual_available']

class ProductProduct(models.Model):
    _inherit = "product.product"


    global_qty_available = fields.Float(
        'Quantity On Hand', compute='_compute_quantities', search='_search_qty_available',
        digits=dp.get_precision('Product Unit of Measure'),
        compute_sudo=True)
    global_virtual_available = fields.Float(
        'Forecast Quantity', compute='_compute_quantities', search='_search_virtual_available',
        digits=dp.get_precision('Product Unit of Measure'),
        compute_sudo=True)
    global_incoming_qty = fields.Float(
        'Incoming', compute='_compute_quantities', search='_search_incoming_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        compute_sudo=True)
    global_outgoing_qty = fields.Float(
        'Outgoing', compute='_compute_quantities', search='_search_outgoing_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        compute_sudo=True)

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_quantities(self):
        res = self.compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'),
                                            self._context.get('package_id'), self._context.get('from_date'),
                                            self._context.get('to_date'))
        for product in self:
            product.global_qty_available = res[product.id]['qty_available']
            product.global_incoming_qty = res[product.id]['incoming_qty']
            product.global_outgoing_qty = res[product.id]['outgoing_qty']
            product.global_virtual_available = res[product.id]['virtual_available']

