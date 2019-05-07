# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order_type = request.env['crm.team'].sudo().search([('id', '=', vals['team_id'])]).team_type
        if order_type == 'website':
            website = request.env['website'].get_current_website()
            type_id = website.sale_type_id
            if type_id:
                vals.update({
                    'type_id': type_id.id
                })
        return super(SaleOrder, self).create(vals)
