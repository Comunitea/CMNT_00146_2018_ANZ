# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):

        team_id = vals.get('team_id', False)
        domain = []
        if team_id:
            domain = [('id', '=', team_id)]
        order_type = request.env['crm.team'].sudo().search(domain, limit=1).team_type
        if order_type == 'website':
            website = request.env['website'].get_current_website()
            type_id = website.sale_type_id
            if type_id:
                vals.update({
                    'type_id': type_id.id
                })

        return super(SaleOrder, self).create(vals)
