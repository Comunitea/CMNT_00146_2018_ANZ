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
    def check_payment_term(self, payment_term_id=False):
        limit = float(self.env['ir.config_parameter'].sudo().get_param('account_invoice.amount_untaxed_limit', 100))
        greater = payment_term_id or int(self.env['ir.config_parameter'].sudo().get_param('account_invoice.amount_untaxed_greater', 9))
        less = int(self.env['ir.config_parameter'].sudo().get_param('account_invoice.amount_untaxed_less', 16))
        for inv in self.filtered(lambda x: x.type == 'out_invoice'):
            if inv.amount_untaxed > limit:
                term = greater
            else:
                term = less

            inv.payment_term_id = self.env['account.payment.term'].browse(term)

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'amount_untaxed' in vals:
            for inv in self.filtered(lambda x: x.type == 'out_invoice'):
                inv.check_payment_term()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

