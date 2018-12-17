# -*- coding: utf-8 -*-

from odoo import api, models


class SaleCommissionMixin(models.AbstractModel):
    _inherit = "sale.commission.mixin"

    @api.model
    def _prepare_agents_vals_by_brand(self, partner, product):
        res = super()._prepare_agents_vals()
        brand = product.product_brand_id
        if not brand:
            return res
        agent_vals = []
        agents = partner.get_brand_agents(brand.id)
        if not agents:
            agents = partner.agents

        for agent in agents:
            commission = agent.get_brand_commission(brand.id)
            if not commission:
                commission = agent.commission

            values = (0, 0, {'agent': agent.id, 'commission': commission.id})
            agent_vals.append(values)
        res = agent_vals
        return res


class SaleOrderLineAgent(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"

    @api.onchange('agent')
    def onchange_agent(self):
        super(SaleOrderLineAgent, self).onchange_agent()
        if self.object_id.product_id.product_brand_id:
            brand = self.object_id.product_id.product_brand_id
            commission_id = self.agent.get_brand_commission(brand.id)
            if not commission_id:
                commission_id = self.agent.commission.id
        self.commission = commission_id
