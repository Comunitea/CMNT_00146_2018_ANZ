# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _


class BlogPost(models.Model):
    _inherit = 'blog.post'

    only_affiliates = fields.Boolean(string=_("Only available for affiliate partners"), default=False)
