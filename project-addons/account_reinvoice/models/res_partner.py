# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductBrand(models.Model):
    _inherit = 'res.partner'

    reinvoice_rule_ids = fields.One2many(
        'reinvoice.rule', 'partner_id', 'Reinvoice Rules')
    reinvoice_rules_count = fields.Integer('# Rules',
                                           compute='_count_reinvoice_rules')

    @api.multi
    def get_reinvoice_discount(self, line):
        import ipdb; ipdb.set_trace()
        self.ensure_one()

        partner_id = line.invoice_id.partner_id
        product_id = line.product_id
        scheduled_sale = product_id and product_id.scheduled_sale_id and True or False

        domain = ['|', ('partner_id', '=', partner_id.id), ('partner_id', '=', False),
                  '|', ('brand_id', '=', product_id.product_brand_id.id), ('brand_id', '=', False),
                  ('scheduled_sale', '=', scheduled_sale),
                  ('affiliate', '=', partner_id.affiliate),
                  ('supplier_discount', '=', line.discount)]
        rule = self.env['reinvoice.rule'].search(domain, order='partner_id desc, brand_id desc')
        print (rule.mapped('id'))
        if not rule:
            print ('No encuentro regla')
            return line.discount
        res = rule[0]
        print ('Regla {} para {} :{} '.format(res.id, res.partner_id, res.customer_discount))
        return res.customer_discount

    @api.multi
    def _count_reinvoice_rules(self):
        for partner in self:
            domain = [('partner_id', '=', partner.id)]
            count = self.env['reinvoice.rule'].search_count(domain)
            partner.reinvoice_rules_count = count

    @api.multi
    def action_view_reinvoice_rules(self):
        """
        Smart button: View the reinvoice rules
        """
        self.ensure_one()
        domain = [('partner_id', '=', self.id)]
        rules = self.self.env['reinvoice.rule'].search(domain)
        action = self.env.ref('account_reinvoice.action_reinvoice_rules').\
            read()[0]
        if action:
            action['domain'] = [('id', 'in', rules.ids)]
            action['context'] = {'default_partner_id': self.id}
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


