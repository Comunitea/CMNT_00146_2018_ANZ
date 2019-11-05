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

    def dynamic_category_list(self):
        domain = ['|', ('website_ids', '=', False), ('website_ids', 'in', self.id)]
        return self.env['product.public.category'].sudo().search(domain)


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

    dynamic_cat_menu = fields.Boolean(string='Dynamic categories menu', default=False)
