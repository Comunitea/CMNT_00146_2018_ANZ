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
        active_model = self._context.get('active_model', False)

        if active_model:
            record = self.env[active_model].browse(self._context['active_id'])
            if 'scheduled_sale_id' in record._fields and record.scheduled_sale_id:
                schedule_domain = [('scheduled_sale_id', '=', record.scheduled_sale_id)]
                if record.scheduled_sale_id.product_brand_id:
                    brand_domain = [('product_brand_id', '=', record.scheduled_sale_id.product_brand_id.id)]
                    args = expression.AND([args, brand_domain])
            else:
                schedule_domain = [('scheduled_sale_id', '=', False)]
            args = expression.AND([args, schedule_domain])
        return args
