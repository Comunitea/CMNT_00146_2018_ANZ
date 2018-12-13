# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductBrand(models.Model):
    _inherit = 'res.partner'

    reinvoice_rule_ids = fields.One2many(
        'reinvoice.rule', 'brand_id', 'Reinvoice Rules')
    reinvoice_rules_count = fields.Integer('# Rules',
                                           compute='_count_reinvoice_rules')

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
