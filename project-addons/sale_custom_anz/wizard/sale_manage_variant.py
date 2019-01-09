# -*- coding: utf-8 -*-
# © 2018 Comunitea - Omar Castiñeira Saavedra <omar@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models

class SaleManageVariant(models.TransientModel):

    _inherit = 'sale.manage.variant'

    @api.model
    def _get_default_partner(self):
        if self._context.get('active_id', False) and \
                self._context.get('active_model', False):
            if self._context['active_model'] == 'sale.order':
                active_id = self._context['active_id']
            elif self._context['active_model'] == 'sale.order.line':
                line_id = self._context['active_id']
                active_id = self.env['sale.order.line'].browse(line_id).\
                    order_id.id

            if active_id:
                order = self.env['sale.order'].browse(active_id)
                return order.partner_id.commercial_partner_id.id
            return False

    partner_id = fields.Many2one("res.partner", "Customer",
                                 default=_get_default_partner)

    default_variant_id = fields.Many2one(comodel_name='product.attribute')

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
       if self.product_tmpl_id and len(self.product_tmpl_id.attribute_line_ids)==1:

           self.default_variant_id = self.product_tmpl_id.attribute_line_ids.attribute_id
           print (self.default_variant_id)
       super(SaleManageVariant, self)._onchange_product_tmpl_id()

    @api.model
    def default_get(self, fields):
        res = super(SaleManageVariant, self).default_get(fields)
        return res