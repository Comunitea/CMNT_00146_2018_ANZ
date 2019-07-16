# -*- coding: utf-8 -*-

import json
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.seo_base.controllers.redirecting import ProductRedirect
from odoo.osv import expression


class WebsiteSaleExtended(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values):
        """
            Modifica el domain original para mostrar los productos en funcion de los nuevos subdominios.
            domain_swp: controla que no se muestren los productos sin stock en conjunto con el cron act_stock_published
            de product.py. El resto de domains solo busca dentro de esos ids.
            attr_domain: para buscar productos dentro del contexto por filtros de atributos.
            search: pasa del contexto y realiza la busqueda por los terminos introducidos en el search box.

        """
        # Set fuzzy search for more results
        request.env.cr.execute("SELECT set_limit(0.2);")
        domain_origin = super(WebsiteSaleExtended, self)._get_search_domain(search, category, attrib_values)
        attr_domain = []
        has_att_filter = False
        filter_args = request.httprequest.args

        # Search and filters work together
        if search and search != 0:
            for srch in search.split(" "):
                domain_search = ['|', '|', '|', '|', '|', '|',
                                 ('name', '%', srch),
                                 ('ref_template', 'ilike', srch),
                                 ('product_color', 'ilike', srch),
                                 ('product_variant_ids.attribute_value_ids', 'ilike', srch),
                                 ('public_categ_ids.complete_name', 'ilike', srch),
                                 ('public_categ_ids.public_categ_tag_ids', 'ilike', srch),
                                 # ('product_variant_ids', 'ilike', srch),
                                 ('product_variant_ids.product_brand_id', 'ilike', srch)]
                domain_origin = expression.normalize_domain(domain_origin)
                domain_origin = expression.OR([domain_origin, domain_search])

        if filter_args:
            brand = int(filter_args.get('brand', False))
            context = dict(request.env.context)
            if context.get('brand_id') == 0:
                context.pop('brand_id')
                domain_origin.remove([d for d in domain_origin if 'product_brand_id' in d][0])
            if brand and brand != 0:
                domain_origin.append(('product_brand_id', '=', brand))

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

        # Only can put on context products with stock > 0 or with stock = 0 but published
        # search and filters and all domain have to respect this. So that we need add this like an AND
        website = request.website
        domain_swp = [('website_id', '=', website.id), ('stock_website_published', '=', True)]
        product_ids = request.env['template.stock.web'].sudo().search(domain_swp).mapped('product_id').ids
        domain_origin += [('id', 'in', product_ids)]

        return domain_origin

    @http.route(['/shop/cart/multi_update'], type='json', auth="public", methods=['POST'], website=True)
    def multi_update_cart(self, update_data, product_template):
        """
            Añade multiples variantes de una plantilla al carrito
        """
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

            for key in variants:
                qty = variants[key]
                line_id = None
                attr_name = ''

                if len(variant_ids) == 1 and variant_ids.id == int(key, 10):
                    # Search product.product for a non-variants template
                    product_id = request.env['product.product'].sudo().search([('id', '=', variant_ids.id)])
                    attr_name = '<strong>%s</strong>' % product_id.name
                else:
                    # Search product.product with current attributes for multi-variant template
                    product_id = variant_ids.filtered(lambda x: int(key, 10) in x.attribute_value_ids.ids)
                    if product_id:
                        attr_name = product_id.attribute_value_ids.sudo().search([('id', '=', int(key, 10))], limit=1).name
                        attr_name = '<strong>%s</strong>' % attr_name

                if product_id:
                    # Check of product in stock and shop cart
                    max_qty = product_id.sudo().get_web_max_qty()
                    product_line = order.order_line.filtered(lambda x: x.product_id == product_id)
                    cart_qty = product_line and product_line[0].product_uom_qty or 0
                    if cart_qty:
                        line_id = product_line.id

                    if max_qty >= 0 and (max_qty - cart_qty - qty < 0):
                        in_cart_msg = _('and %d unit(s) are already in cart')
                        ask_msg = _('<p class="alert alert-warning">%s: Ask for %d units but only %d is available %s</p>')
                        in_cart = in_cart_msg % cart_qty if cart_qty > 0 else ''
                        prod_list += ask_msg % (attr_name, qty, max_qty, in_cart)
                        qty = min(qty, max_qty)
                    else:
                        if cart_qty > 0:
                            but_msg = _('<p class="alert alert-warning">%s: Added %d unit(s) but %d unit(s) was already in your cart</p>')
                            prod_list += but_msg % (attr_name, qty, cart_qty)
                        else:
                            prod_list += _('<p class="alert alert-success">%s: Added %d unit(s)</p>') % (attr_name, qty)

                    # Add to cart
                    if qty > 0:
                        order._cart_update(product_id=product_id.id, line_id=line_id, add_qty=qty)
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


class ProductRedirectContext(ProductRedirect):
    def _update_context(self):
        """
        Update request.env.context to keep in redirections and super calls
        """
        context = dict(request.env.context)
        context.update({
            # Show product stock by website warehouse
            'warehouse': request.website.warehouse.id
        })
        request.env.context = context
        return
