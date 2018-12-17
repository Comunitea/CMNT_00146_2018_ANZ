# -*- coding: utf-8 -*-

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_agents_vals(self):
        self.ensure_one()
        super()._prepare_agents_vals()
        return self._prepare_agents_vals_by_brand(
            self.order_id.partner_id, self.product_id
        )

    @api.model
    def create(self, vals):
        product_id = vals.get('product_id', False)
        order_id = vals.get('order_id', False)
        if order_id and product_id:
            partner = self.env['sale.order'].browse(order_id).partner_id
            product = self.env['product.product'].browse(product_id)
            agent_vals = self._prepare_agents_vals_by_brand(
                partner, product)
            vals['agents'] = agent_vals
        return super().create(vals)

    @api.multi
    def write(self, vals):
        self2 = self.env['sale.order.line']
        if vals.get('product_id'):
            for line in self:
                if line.product_id.id != vals['product_id']:
                    self2 += line
        res = super().write(vals)
        self2.recompute_agents()
        return res

    # @api.multi
    # @api.onchange('product_id')
    # def product_id_change(self):
    #     res = super(SaleOrderLine, self).product_id_change()
    #     partner = self.order_id.partner_id
    #     brand = self.product_id.product_brand_id
    #     if not brand:
    #         return res
    #     agent_vals = []
    #     agents = partner.get_brand_agents(brand.id)
    #     if not agents:
    #         agents = partner.agents

    #     for agent in agents:
    #         commission_id = agent.get_brand_commission(brand.id)
    #         if not commission_id:
    #             commission_id = agent.commission.id

    #         values = (0, 0, {'agent': agent.id, 'commission': commission_id})
    #         agent_vals.append(values)
    #     self.update({'agents': agent_vals})
    #     return res
