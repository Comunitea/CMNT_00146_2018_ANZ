# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductBrand(models.Model):
    _inherit = 'product.brand'

    reinvoice_rule_ids = fields.One2many(
        'reinvoice.rule', 'brand_id', 'Reinvoice Rules')
    reinvoice_rules_count = fields.Integer('# Rules',
                                           compute='_count_reinvoice_rules')

    @api.multi
    def _count_reinvoice_rules(self):
        for brand in self:
            domain = [('brand_id', '=', brand.id)]
            count = self.env['reinvoice.rule'].search_count(domain)
            brand.reinvoice_rules_count = count

    @api.multi
    def get_reinvoice_discount(self, line):
        self.ensure_one()
        res = 0.0  # Todo, que pasa si no encuentro
        partner_id = line.invoice_id.partner_id.id
        # Search specific by customer first
        rule = self.reinvoice_rule_ids.filtered(
            lambda r: r.partner_id.id == partner_id and
            r.supplier_discount == line.discount)
        if not rule:
            rule = self.reinvoice_rule_ids.filtered(
                lambda r: r.partner_id.id is False and
                r.supplier_discount == line.discount)
        if not rule:
            raise UserError(
                _('No reinvoice rule founded for discount of %s')
                % line.discount)
        res = rule[0].customer_discount
        return res

    @api.multi
    def action_view_reinvoice_rules(self):
        """
        Smart button: View the reinvoice rules
        """
        self.ensure_one()
        rules = self.reinvoice_rule_ids
        action = self.env.ref('account_reinvoice.action_reinvoice_rules').\
            read()[0]
        if action:
            action['domain'] = [('id', 'in', rules.ids)]
            action['context'] = {'default_brand_id': self.id}
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
