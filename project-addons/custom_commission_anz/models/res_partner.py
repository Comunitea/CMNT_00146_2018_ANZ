# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.osv import expression


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    def _count_commissions(self):
        for brand in self:
            domain = ['|', ('partner_id', '=', brand.id),
                      ('partner_id', '=', False)]
            count = self.env['commission.brand'].search_count(domain)
            brand.commission_rules_count = count

    agent_brand_ids = fields.One2many(
        'agent.brand', 'partner_id', 'Agents by brand')
    commission_brand_ids = fields.One2many(
        'commission.brand', 'partner_id', 'Comissions by brand')

    commission_rules_count = fields.Integer('# Commissions',
                                            compute='_count_commissions')

    @api.multi
    def action_view_commissions(self):
        self.ensure_one()
        domain = ['|', ('partner_id', '=', self.id),
                  ('partner_id', '=', False)]
        commission_rules = self.env['commission.brand'].search(domain)
        action = self.env.ref(
            'custom_commission_anz.action_commission_by_brand').read()[0]
        action['domain'] = [('id', 'in', commission_rules.ids)]
        action['context'] = {'default_partner_id': self.id, 
                             'search_default_partner_id': self.id}
        return action

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
    def get_brand_commission(self, brand_id, discount=0.0):
        """
        Returns agent commission for a specific brand
        """
        res = False
        self.ensure_one()

        # Busca un descuento menor o igual que el indicado, por marca, 
        # por agente, o sin alguno de ellos
        domain_specific = [
            ('discount', '<=', discount),
            '|',
            ('brand_id', '=', brand_id),
            ('brand_id', '=', False),
            '|',
            ('partner_id', '=', self.id),
            ('partner_id', '=', False)]

        # Busca un descuento menor o igual que el indicado generico, sin marca
        # ni agente
        domain_generic = [
            ('partner_id', '=', False), ('brand_id', '=', False), 
            ('discount', '<=', discount)
        ]
        d1 = expression.normalize_domain(domain_specific)
        d2 = expression.normalize_domain(domain_generic)
        domain = expression.OR([d1, d2])

        # Ordeno primero los que tienen agente, luego sin el, lo mismo para
        # marca, y dentro de estos los descuentos van de mayor a menor para
        # coger el mas cercano, SE DEVUELVE ORDENADO ASÍ:
        # AENTE ESTABLECIDO   MARCA ESTABLECIDA
        #       SI                   SI
        #       SI                   NO
        #       NO                   SI
        #       NO                   NO
        commission_rules = self.env['commission.brand'].search(
            domain, order='partner_id asc, brand_id asc, discount desc')
        if commission_rules:
            res = commission_rules[0].commission_id
        return res
