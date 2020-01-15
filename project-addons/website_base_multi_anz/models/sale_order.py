# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        ctx = self.env.context.copy()
        from_website = ctx.get('from_website', False)

        if from_website:
            team_id = vals.get('team_id', False)
            domain = []
            if team_id:
                domain = [('id', '=', team_id)]
            type_id = self.recalculate_type_id(domain)
            if type_id:
                vals.update({
                    'type_id': type_id.id
                })

        return super(SaleOrder, self).create(vals)

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.team_id:
            domain = [('id', '=', self.team_id.id)]
            type_id = self.recalculate_type_id(domain)
            if type_id:
                self.type_id = type_id.id

    def recalculate_type_id(self, domain):
        order_type = request.env['crm.team'].sudo().search(domain, limit=1).team_type
        if order_type == 'website':
            website = request.env['website'].get_current_website()
            return website.sale_type_id