# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    agent_brand_ids = fields.One2many(
        'agent.brand', 'partner_id', 'Agents by brand')
    commission_brand_ids = fields.One2many(
        'commission.brand', 'partner_id', 'Comissions by brand')

    @api.multi
    def get_brand_agents(self, brand_id):
        """
        Returns agent commission for a specific brand
        """
        res = False
        self.ensure_one()
        brand_agent = self.agent_brand_ids.\
            filtered(lambda b: b.brand_id.id == brand_id)
        if brand_agent:
            res = brand_agent[0].agent_ids
        return res

    @api.multi
    def get_brand_commission(self, brand_id):
        """
        Returns agent commission for a specific brand
        """
        res = False
        self.ensure_one()
        brand_commission = self.commission_brand_ids.\
            filtered(lambda b: b.brand_id.id == brand_id)
        if brand_commission:
            res = brand_commission[0].commission_id
        return res


class AgentBrand(models.Model):

    _name = 'agent.brand'

    partner_id = fields.Many2one('res.partner', 'Partner',)
    brand_id = fields.Many2one('product.brand', 'Brand')
    agent_ids = fields.Many2many(
        comodel_name="res.partner", relation="agent_brand_rel",
        column1="agent_brand_id", column2="agent_id",
        domain=[('agent', '=', True)])


class CommissionBrand(models.Model):

    _name = 'commission.brand'

    partner_id = fields.Many2one('res.partner', 'Partner',)
    brand_id = fields.Many2one('product.brand', 'Brand')
    commission_id = fields.Many2one('sale.commission', 'Commission')
