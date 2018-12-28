# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models


class SaleManageVariant(models.TransientModel):
    _inherit = 'sale.manage.variant'

    @api.model
    def _get_default_scheduled_sale_id(self):
        if self._context.get('scheduled_sale_id', False):
            return self._context['scheduled_sale_id']
        order = False
        if self._context.get('active_model') == 'sale.order':
            active_id = self._context['active_id']
            order = self.env['sale.order'].browse(active_id)
        elif self._context.get('active_model') == 'sale.order.line':
            line_id = self._context['active_id']
            order = self.env['sale.order.line'].browse(line_id).\
                order_id
        return order and order.scheduled_sale_id and order.scheduled_sale_id.id or False

    scheduled_sale_id = fields. \
        Many2one('scheduled.sale', 'Schedule order', readonly=True,  default=_get_default_scheduled_sale_id)

