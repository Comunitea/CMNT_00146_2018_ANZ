# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields

class ProcurementGroup(models.Model):
    _inherit = "procurement.group"


    @api.model
    def create(self, vals):
        res = super(ProcurementGroup, self).create(vals)
        return res

class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values,
                               group_id):
        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom,
                                                                     location_id, name, origin, values, group_id)
        result.update({'scheduled_sale_id': values.get('scheduled_sale_id', False),
                       'deliver_month': values.get('deliver_month', '')})
        return result