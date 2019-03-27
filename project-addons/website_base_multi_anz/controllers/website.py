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
            prod_list = ''
            # Search product.product with current attributes
            for key in variants:
                qty = variants[key]
                product_id = variant_ids.filtered(lambda x: int(key, 10) in x.attribute_value_ids.ids)
                if product_id:
                    # Add to cart
                    order._cart_update(product_id=product_id.id, add_qty=qty)
                    qty_total += qty
                    attr_name = product_id.attribute_value_ids.search([('id', '=', int(key, 10))], limit=1).name
                    prod_list += '<li>%s <strong>(%s)</strong>: %d unit(s)</li>' % (product_id.name, attr_name, qty)
            if qty_total > 0:
                success = True
                message = _('<p>Was added %d unit(s):</p><ul>%s</ul>' % (qty_total, prod_list))
                quantity = order.cart_quantity
            else:
                message = _('Product variants not found')
        else:
            message = _('Empty list of product variants')

        # Return fail/success message
        values = {
            'success': success,
            'quantity': quantity,
            'message': message
        }
        return json.dumps(values)
