# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    sponsored = fields.Boolean(readonly=True, states={'draft': [('readonly', False)]}, copy=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.player:
            self.sponsored = True

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if res.partner_id.player and res.amount_total <= res.partner_id.sponsorship_bag:
            res.sponsored = True
        return res

    def action_invoice_open(self):
        if self.sponsored:
            if self.type == 'out_invoice':
                self.partner_id.decrease_bag(self.amount_total)
            else:
                self.partner_id.decrease_bag(-self.amount_total)
        return super(AccountInvoice, self).action_invoice_open()

    def action_invoice_cancel(self):
        if self.sponsored:
            if self.type == 'out_invoice':
                self.partner_id.decrease_bag(-self.amount_total)
            else:
                self.partner_id.decrease_bag(self.amount_total)
        return super(AccountInvoice, self).action_invoice_cancel()
