# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def add_args_to_product_search(self, args=[]):
        args = super(ResPartner, self).add_args_to_product_search(args=args)
        return args
