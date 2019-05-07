# -*- coding: utf-8 -*-

import json
from odoo import http, _
from odoo.osv import expression
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleExtended(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values):
        domain = super(WebsiteSaleExtended, self)._get_search_domain(search, category, attrib_values)
        domain = expression.normalize_domain(domain)

        if search:
            domain_search = []
            for srch in search.split(" "):
                domain_search += ['|', '|', '|', '|',
                                  ('product_variant_ids.attribute_value_ids', 'ilike', srch),
                                  ('public_categ_ids', 'ilike', srch),
                                  ('public_categ_ids.public_categ_tag_ids', 'ilike', srch),
                                  ('product_variant_ids', 'ilike', srch),
                                  ('product_variant_ids.product_brand_id', 'ilike', srch)]
            domain = expression.OR([domain, domain_search])

        if category:
            categories = request.env['product.public.category']
            # Search sub-categories of first and second depth level
            sub_cat_l1 = categories.sudo().search([('parent_id', '=', int(category))], order='sequence')
            sub_cat_l2 = categories.sudo().search([('parent_id', 'in', sub_cat_l1.ids)], order='sequence')
            # Create new list of categories to show
            list_cat = [int(category)]
            list_cat.extend(sub_cat_l1.ids)
            list_cat.extend(sub_cat_l2.ids)
            # Search products from sub-categories of first and second depth level
            domain += [('public_categ_ids', 'in', list_cat)]

        return domain

    @http.route(['/shop/cart/multi_update'], type='json', auth="public", methods=['POST'], website=True)
    def multi_update_cart(self, update_data, product_template):
        """ Añade multiples variantes de una plantilla al carrito """
        success = False
        quantity = 0
        variants = json.loads(update_data)
        template = request.env['product.template'].search([('id','=',product_template)])
        variant_ids = template.product_variant_ids

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
                    attr_name = product_id.attribute_value_ids.sudo().search([('id', '=', int(key, 10))], limit=1).name
                    attr_name = '<strong>%s</strong>' % attr_name
                    # Check of product stock
                    max_qty = -1
                    if product_id.inventory_availability in ['always', 'threshold']:
                        max_qty = max(0,product_id.sudo().qty_available - product_id.sudo().outgoing_qty)
                    elif product_id.inventory_availability in ['always_virtual','threshold_virtual']:
                        max_qty = max(0,product_id.sudo().virtual_available)
                    threshold = template.available_threshold
                    if product_id.inventory_availability in ['threshold','threshold_virtual'] and treshold > 0:
                        max_qty = max(0,max_qty - threshold)
                    # Search this variant qty in the cart
                    for line in order.order_line:
                        if line.product_id == product_id:
                            cart_qty = line.product_uom_qty

                    if max_qty >= 0 and max_qty - cart_qty - qty < 0:
                        prod_list += _('<p class="alert alert-warning">{}: you ask for {} units but only {} '
                                       'is available</p>'.format(attr_name, qty+cart_qty, max_qty))
                        qty = min(qty, max_qty)
                    else:
                        prod_list += _('<p class="alert alert-success">%s: %d unit(s)</p>') % (attr_name, qty)
                    # Add to cart
                    if qty > 0:
                        order._cart_update(product_id=product_id.id, add_qty=qty)
                        qty_total += qty

            if qty_total > 0:
                success = True
                message = _('<p><strong>Was added %d unit(s) of %s:</strong></p>%s') % (
                    qty_total, curr_prod.name, prod_list)
                quantity = order.cart_quantity
            else:
                message = _('<p><strong>Product variants for %s not found:</strong></p>%s') % (
                    curr_prod.name, prod_list)
        else:
            message = _('<p><strong>Empty list of product variants</strong></p>')

        # Return fail/success message
        values = {
            'success': success,
            'quantity': quantity,
            'message': message
        }
        return json.dumps(values)
