# -*- coding: utf-8 -*-

import json
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class MultiUpdateCart(WebsiteSale):

    @http.route(['/shop/cart/multi_update'], type='json', auth="public", methods=['POST'], website=True)
    def multi_update_cart(self, update_data, product_template):
        success = False
        quantity = 0
        variants = json.loads(update_data)
        products = request.env['product.template']
        domain = [('id', '=', product_template)]
        curr_prod = products.search(domain)
        variant_ids = curr_prod.product_variant_ids

        if variants and len(variants) > 0:
            # Set order data
            order = request.website.sale_get_order(force_create=True)
            qty_total = 0

            for key in variants:
                qty = variants[key]
                product_id = variant_ids.filtered(lambda x: int(key, 10) in x.attribute_value_ids.ids)
                if product_id:
                    order._cart_update(product_id=product_id.id, add_qty=qty)
                    qty_total += qty
            if qty_total > 0:
                success = True
                message = _('Was added %d unit(s)' % qty_total)
                quantity = order.cart_quantity
            else:
                message = _('Product variants not found')
        else:
            message = _('Empty list of product variants')

        values = {
            'success': success,
            'quantity': quantity,
            'message': message
        }
        return json.dumps(values)
