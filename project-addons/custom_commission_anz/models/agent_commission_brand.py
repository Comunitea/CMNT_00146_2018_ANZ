# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AgentBrand(models.Model):

    _name = 'agent.brand'

    partner_id = fields.Many2one('res.partner', 'Customer',
                                 domain=[('customer', '=', True)])
    brand_id = fields.Many2one('product.brand', 'Brand')
    agent_ids = fields.Many2many(
        comodel_name="res.partner", relation="agent_brand_rel",
        column1="agent_brand_id", column2="agent_id",
        domain=[('agent', '=', True)])


class CommissionBrand(models.Model):

    _name = 'commission.brand'

    _order = 'partner_id asc, brand_id asc, discount desc'

    partner_id = fields.Many2one('res.partner', 'Agent',
                                 domain=[('agent', '=', True)])
    brand_id = fields.Many2one('product.brand', 'Brand')
    discount = fields.Float('From Discount', default=0.0)
    commission_id = fields.Many2one('sale.commission', 'Commission')

    _sql_constraints = [
        ('unique_agent_brand_discount',
         'unique(partner_id, brand_id, discount)',
         _("You can not define same, agent, brand and from discount rule")),
    ]
