# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        res.check_payment_term()
        return res

    @api.multi
    def action_invoice_open(self):
        self.check_payment_term()
        return super().action_invoice_open()

    @api.multi
    def check_payment_term(self):
        rule_ids = self.env['payment.term.rule']
        for inv in self:
            rule = rule_ids.get_payment_term_rule(inv)
            if rule:
                message = "Change {} to {}".format(inv.payment_term_id.name, rule.new_payment_term_id.name)
                inv.payment_term_id = rule.new_payment_term_id
                inv.message_post(message)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

