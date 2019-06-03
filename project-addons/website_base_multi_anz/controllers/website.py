# -*- coding: utf-8 -*-

import json
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleExtended(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values):
        domain_origin = super(WebsiteSaleExtended, self)._get_search_domain(search, category, attrib_values)
        attr_domain = []
        has_att_filter = False
        filter_args = request.httprequest.args

        if filter_args:
            brand = int(filter_args.get('brand', False))
            context = dict(request.env.context)
            if context.get('brand_id') == 0:
                context.pop('brand_id')
                domain_origin.remove([d for d in domain_origin if 'product_brand_id' in d][0])

            tags = request.env['product.attribute.tag'].sudo()

            gender = filter_args.get('gender', False)
            if gender:
                gender_domain = ['&', ('type', '=', 'gender'), ('value', '=', gender)]
                if brand and brand != 0:
                    gender_domain += [('product_brand_id', '=', brand)]
                tag_gender = tags.search(gender_domain)
                if tag_gender:
                    attr_domain += [('product_gender_id', 'in', tag_gender.ids)]
                    has_att_filter = True

            age = filter_args.get('age', False)
            if age:
                tag_domain = ['&', ('type', '=', 'age'), ('value', '=', age)]
                if brand and brand != 0:
                    tag_domain += [('product_brand_id', '=', brand)]
                tag_age = tags.search(tag_domain)
                if tag_age:
                    attr_domain += [('product_age_id', 'in', tag_age.ids)]
                    has_att_filter = True

        if has_att_filter:
            product_attributes = request.env['product.attribute'].sudo().search(attr_domain)
            product_attribute_lines = request.env['product.attribute.line'].sudo().search([
                ('attribute_id', 'in', product_attributes.ids)
            ])
            domain_origin += [('attribute_line_ids', 'in', product_attribute_lines.ids)]

        if search:
            for srch in search.split(" "):
                domain_origin.insert(-1, '|')
                domain_origin += ['|', '|', '|', '|',
                                  ('product_variant_ids.attribute_value_ids', 'ilike', srch),
                                  ('public_categ_ids.complete_name', 'ilike', srch),
                                  ('public_categ_ids.public_categ_tag_ids', 'ilike', srch),
                                  ('product_variant_ids', 'ilike', srch),
                                  ('product_variant_ids.product_brand_id', 'ilike', srch)]

        return domain_origin

    @http.route(['/shop/cart/multi_update'], type='json', auth="public", methods=['POST'], website=True)
    def multi_update_cart(self, update_data, product_template):
        """ Añade multiples variantes de una plantilla al carrito """
        success = False
        quantity = 0
        variants = json.loads(update_data)
        template = request.env['product.template'].search([('id', '=', product_template)])
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
                    cart_qty = 0
                    if product_id.inventory_availability in ['always', 'threshold']:
                        max_qty = max(0, product_id.sudo().qty_available - product_id.sudo().outgoing_qty)
                    elif product_id.inventory_availability in ['always_virtual', 'threshold_virtual']:
                        max_qty = max(0, product_id.sudo().virtual_available)

                    threshold = template.sudo().available_threshold
                    if product_id.inventory_availability in ['threshold', 'threshold_virtual'] and threshold > 0:
                        max_qty = max(0, max_qty - threshold)

                    # Search this variant qty in the cart
                    for line in order.order_line:
                        if line.product_id == product_id:
                            cart_qty = line.product_uom_qty

                    if max_qty >= 0 and (max_qty - cart_qty - qty < 0):
                        prod_list += _(
                            '<p class="alert alert-warning">%s: Ask for %d units but only %d is available</p>' % (
                                attr_name, (qty + cart_qty), max_qty))
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
                    qty_total, template.name, prod_list)
                quantity = order.cart_quantity
            else:
                message = _('<p><strong>Product for %s not found:</strong></p>%s') % (template.name, prod_list)
        else:
            message = _('<p><strong>Empty product list</strong></p>')

        # Return fail/success message
        values = {
            'success': success,
            'quantity': quantity,
            'message': message
        }
        return json.dumps(values)

    def _get_search_order(self, post):
        return '%s , id asc' % post.get('order', 'website_sequence asc')

    @http.route(['/shop/cart/create_order'], type='json', auth="public", methods=['POST'], website=True)
    def multi_update_create_order(self):
        order = request.website.sale_get_order(force_create=True)
        result = True if order else False
        return result
