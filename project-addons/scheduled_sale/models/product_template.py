# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')
    origin_scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')



class ProductProduct(models.Model):

    _inherit = 'product.product'

    #scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order', readonly=True)
    #origin_scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order', readonly=True)




