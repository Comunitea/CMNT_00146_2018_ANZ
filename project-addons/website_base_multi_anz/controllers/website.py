# -*- coding: utf-8 -*-

import json
import shlex

from odoo import http, _
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import Website
from odoo.addons.seo_base.controllers.redirecting import ProductRedirect
from odoo.addons.website_form_recaptcha.controllers.main import WebsiteForm


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

        # Search and filters work together
        if search and search != 0:
            for srch in shlex.split(search):
                if len(srch) > 2:
                    domain_search = ['|', '|', '|', '|', '|',
                                     ('name', '%', srch),
                                     ('ref_template', 'ilike', srch),
                                     ('attribute_line_ids', 'ilike', srch),
                                     ('product_variant_ids.attribute_value_ids.range_search', 'ilike', srch),
                                     ('public_categ_ids.complete_name', 'ilike', srch),
                                     ('public_categ_ids.public_categ_tag_ids', 'ilike', srch)]
                    domain_origin = expression.normalize_domain(domain_origin)
                    domain_origin = expression.OR([domain_origin, domain_search])

        # Only can put on context products with stock > 0 or with stock = 0 but published
        # search and filters and all domain have to respect this. So that we need add this like an AND
        website = request.website
        domain_swp = [('website_id', '=', website.id), ('stock_website_published', '=', True)]
        product_ids = request.env['template.stock.web'].sudo().search(domain_swp).mapped('product_id').ids
        domain_origin += [('id', 'in', product_ids)]

        # Hide all not published products in website for all employees that they do not web editors
        user = request.env.user
        is_editor_web = user.has_group('website.group_website_publisherl') \
                        or user.has_group('website.group_website_designer')
        if not is_editor_web:
            domain_editor = [('website_published', '=', True)]
            domain_origin = expression.normalize_domain(domain_origin)
            domain_origin = expression.AND([domain_origin, domain_editor])

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
                    product_id = variant_ids.filtered(lambda x: int(key, 10) in x.attribute_value_ids.filtered('main').ids)
                    if product_id:
                        attr_name = product_id.attribute_value_ids.sudo().search([('id', '=', int(key, 10))], limit=1).name
                        attr_name = '<strong>%s</strong>' % attr_name

                if product_id:
                    # Check of product in stock and shop cart by warehouse
                    ctx = request._context.copy()
                    ctx.update(warehouse=request.website.warehouse.id)
                    max_qty = product_id.with_context(ctx).sudo().get_web_max_qty()
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
                        values = order._cart_update(product_id=product_id.id, line_id=line_id, add_qty=qty)
                        message = values.get('warning', '')
                        qty_total += qty

            if qty_total > 0:
                if not message:
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

    def _get_extra_step_multi(self, extra_step):
        if extra_step.multitheme_copy_ids:
            for copy in extra_step.multitheme_copy_ids:
                if copy.website_id and copy.website_id == request.website:
                    return True
        return False

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        """
        Hook to work with extra_option on multi website system.
        """
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.env.ref('website_sale.extra_info_option')
        extra_step_multi = self._get_extra_step_multi(extra_step)
        # Check that extra_info option is activated
        if extra_step.active or extra_step_multi:
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/payment")

    # ------------------------------------------------------
    # Extra step
    # ------------------------------------------------------
    @http.route(['/shop/extra_info'], type='http', auth="public", website=True)
    def extra_info(self, **post):
        """
        Hook to work with extra_option on multi website system.
        """
        # Check that this option is activated
        extra_step = request.env.ref('website_sale.extra_info_option')
        extra_step_multi = self._get_extra_step_multi(extra_step)
        if not extra_step.active and not extra_step_multi:
            return request.redirect("/shop/payment")

        # check that cart is valid
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        # if form posted
        if 'post_values' in post:
            values = {}
            for field_name, field_value in post.items():
                if field_name in request.env['sale.order']._fields and field_name.startswith('x_'):
                    values[field_name] = field_value
            if values:
                order.write(values)
            return request.redirect("/shop/payment")

        values = {
            'website_sale_order': order,
            'post': post,
            'escape': lambda x: x.replace("'", r"\'"),
            'partner': order.partner_id.id,
            'order': order,
        }

        return request.render("website_sale.extra_info", values)


class Website(Website):

    @http.route(['/website/publish/price'], type='http', auth="user", website=True)
    def publish_price(self, access_token=None, **post):
        """
        Gets show/hide prices form by change website_show_price field for partner of request user.
        """
        record = request.env["res.partner"].browse(int(post.get('id', False)))
        if record:
            record.sudo().website_show_price = not record.website_show_price
        return request.redirect(post.get('url', '/shop'))


class WebsiteFormCustom(WebsiteForm):

    def extract_data(self, model, values):
        """
        Inject ReCaptcha validation into pre-existing data extraction.
        Hook to work with website_form_recaptcha into website_form.
        It is needed for activate extra_info view on checkout.
         """
        res = super(WebsiteForm, self).extract_data(model, values)
        # Just read with sudo
        if model.sudo().website_form_recaptcha:
            recaptcha_model = request.env['website.form.recaptcha'].sudo()
            recaptcha_model.validate_request(request, values)
        return res


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
