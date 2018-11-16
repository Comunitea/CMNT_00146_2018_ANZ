# -*- coding: utf-8 -*-

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        partner = self.order_id.partner_id
        brand = self.product_id.product_brand_id
        if not brand:
            return res
        agent_vals = []
        agents = partner.get_brand_agents(brand.id)
        if not agents:
            agents = partner.agents

        for agent in partner.agents:
            commission_id = agent.get_brand_commission(brand.id)
            if not commission_id:
                commission_id = agent.commission.id

            values = (0, 0, {'agent': agent.id, 'commission': commission_id})
            agent_vals.append(values)
        self.update({'agents': agent_vals})
        return res
