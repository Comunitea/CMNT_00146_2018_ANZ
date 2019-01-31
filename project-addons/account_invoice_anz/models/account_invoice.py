# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):

        res = super(AccountInvoice, self).create(vals)
        if res.amount_untaxed < 100:
            payment_term_id = self.env['account.payment.term'].search([('name', '=', '57')], limit=1)
            if payment_term_id:
                res.payment_term_id = payment_term_id
                res.message_post(body="Se aplicado la regla de menos 100 €. Recuerda que no se actualiza al cambiar el importe")
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

