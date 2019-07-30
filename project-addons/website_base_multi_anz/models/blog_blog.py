# -*- coding: utf-8 -*-

from odoo import api, fields, http, models, _


class Blog(models.Model):
    _inherit = 'blog.blog'

    only_affiliates = fields.Boolean(string=_("Only available for affiliate partners"), default=False)
