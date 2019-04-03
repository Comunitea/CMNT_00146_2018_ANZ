# -*- coding: utf-8 -*-

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def onchange_partner_id(self):
        """
        Allways user id in commercial field, avoi to puth the comercial
        assigned to the partner_id
        """
        super(SaleOrder, self).onchange_partner_id()
        self.update({'user_id': self.env.uid})


class SaleOrderLine(models.Model):
    """ cOPIAR ESTA CLASE A ACCOUNT INVOICELINE  para heredar el comportamiento en facturas"""
    _inherit = "sale.order.line"

    def _prepare_agents_vals(self):
        self.ensure_one()
        super()._prepare_agents_vals()
        return self._prepare_agents_vals_by_brand(
            self.order_id.partner_id, self.product_id, 
            self.order_id.user_id.id, self.discount
        )

    @api.model
    def create(self, vals):
        product_id = vals.get('product_id', False)
        order_id = vals.get('order_id', False)
        if order_id and product_id:
            order = self.env['sale.order'].browse(order_id)
            partner = order.partner_id
            product = self.env['product.product'].browse(product_id)
            agent_vals = self._prepare_agents_vals_by_brand( # RECALCULA LAS LINEAS DE AGENTE
                partner, product, order.user_id.id, vals.get('discount', 0.0))
            vals['agents'] = agent_vals
        return super().create(vals)

    @api.multi
    def write(self, vals):
        self2 = self.env['sale.order.line']
        if vals.get('product_id') or 'discount' in vals:
            for line in self:
                if (vals.get('product_id') and
                        line.product_id.id != vals['product_id']) or \
                        vals.get('discount') and \
                        line.discount != vals['discount']:
                    self2 += line
        res = super().write(vals)
        self2.recompute_agents()
        return res
