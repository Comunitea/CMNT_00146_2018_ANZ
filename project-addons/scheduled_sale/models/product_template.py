# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')
    origin_scheduled_sale_id = fields.Many2one('scheduled.sale',
                                               'Schedule order')
