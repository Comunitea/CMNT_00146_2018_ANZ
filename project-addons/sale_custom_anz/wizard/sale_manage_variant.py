# -*- coding: utf-8 -*-
# © 2018 Comunitea - Omar Castiñeira Saavedra <omar@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models

class SaleManageVariant(models.TransientModel):

    _inherit = 'sale.manage.variant'

    @api.model
    def _get_default_partner(self):
        if self._context.get('active_id'):
            order = self.env['sale.order'].browse(self._context['active_id'])
            return order.partner_id.commercial_partner_id.id


    partner_id = fields.Many2one("res.partner", "Customer",
                                 default=_get_default_partner)
