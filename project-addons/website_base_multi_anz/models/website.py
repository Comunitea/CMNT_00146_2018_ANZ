# -*- coding: utf-8 -*-
#
# © 2018 Comunitea - Ruben Seijas <ruben@comunitea.com>
# © 2018 Comunitea - Pavel Smirnov <pavel@comunitea.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http, api, models, fields, _
from odoo.http import request
from odoo.addons.seo_base.models.settings import _default_website


class Website(models.Model):
    """ """

    _inherit = 'website'

    social_twitter = fields.Char(related=False, store=True)
    social_facebook = fields.Char(related=False, store=True)
    social_github = fields.Char(related=False, store=True)
    social_linkedin = fields.Char(related=False, store=True)
    social_youtube = fields.Char(related=False, store=True)
    social_googleplus = fields.Char(related=False, store=True)
    social_instagram = fields.Char(string='Instagram Account')
    email = fields.Char(string='Website Email')

    def _get_warehouse(self):
        return self.env['stock.warehouse'].search([], limit=1)

    warehouse = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse', default=_get_warehouse)

    def _get_order_type(self):
        return self.env['sale.order.type'].search([], limit=1)

    sale_type_id = fields.Many2one('sale.order.type', string='Sale type', default=_get_order_type)

    @api.multi
    def retailer_access(self):
        website = self
        user = request.env.user
        access = True

        if website.name == 'Point Sport':
            is_b2b = user.has_group('sale.group_show_price_subtotal')
            access = True if is_b2b else False

        return access

    @api.multi
    def access_to_blog(self, blog):
        website = self
        user = request.env.user
        access = True

        if website.name == 'Point Sport':
            access = False
            user_b2b = user.has_group('sale.group_show_price_subtotal')
            user_b2c = user.has_group('sale.group_show_price_total') or user.has_group('base.group_public')
            user_admin = user.has_group('website.group_website_publisher') \
                         or user.has_group('website.group_website_designer')

            if (blog.for_retailers and user_b2b) or (blog.for_customers and user_b2c and not user_b2b) or user_admin:
                access = True

            # import ipdb; ipdb.set_trace()

        return access

    def dynamic_category_list(self):
        domain = ['|', ('website_ids', '=', False), ('website_ids', 'in', self.id)]
        return self.env['product.public.category'].sudo().search(domain)

    def product_brand_list(self):
        # .sudo() ?
        return self.env['product.brand'].search([], order='name').filtered(lambda x: x.products_count != 0)

    def product_gender_list(self):
        genders = []
        # .sudo() ?
        gender_list = self.env['product.attribute.tag'].search([('type', '=', 'gender')], order='value')
        # Add gender types to list without duplicate elements
        for gender in gender_list.filtered(lambda x: x.lines_count != 0):
            value = gender.value
            if not genders.count(value) > 0:
                genders.append(value)
        genders.sort()
        return genders

    def product_age_list(self):
        ages = []
        # .sudo() ?
        age_list = self.env['product.attribute.tag'].search([('type', '=', 'age')], order='value')
        # Add age types to list without duplicate elements
        for age in age_list.filtered(lambda x: x.lines_count != 0):
            value = age.value
            if not ages.count(value) > 0:
                ages.append(value)
        ages.sort()
        return ages


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_id = fields.Many2one('website', string="website", default=_default_website, required=True)
    social_instagram = fields.Char(related='website_id.social_instagram')
    email = fields.Char(related='website_id.email')
    sale_type_id = fields.Many2one(related='website_id.sale_type_id')
    inventory_availability = fields.Selection(selection_add=[
        ('always_virtual', _('Show future and current inventory on website and prevent sales if not enough stock')),
        ('threshold_virtual',
         _('Show future and current inventory below a threshold and prevent sales if not enough stock'))
    ])


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    only_retailer = fields.Boolean(string='Only for B2B retailers', default=False)
    not_retailer = fields.Boolean(string='Only for B2C users', default=False)
    website_published = fields.Boolean(string='Published', default=True)
    dynamic_cat_menu = fields.Boolean(string='Dynamic categories menu', default=False)
