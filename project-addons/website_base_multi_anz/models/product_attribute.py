# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    website_published = fields.Boolean(string='Published', default=False)
