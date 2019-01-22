# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
import datetime
import time


import os

class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    date_invoice_from_associate_order = fields.Date(string='Due Date',
         readonly=True, states={'draft': [('readonly', False)]},
         help="Imported form txt import")

    value_date = fields.Date(string='Fecha valor', states={'draft': [('readonly', False)]}, index=True, copy=False)

    def check_existing_txt(self):
        self.env['invoice.txt.import'].import_txt_invoice()

    @api.onchange('payment_term_id', 'date_invoice', 'value_date')
    def _onchange_payment_term_date_invoice(self):
        date_invoice = self.value_date or self.date_invoice
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if not self.payment_term_id:
            # When no payment term defined
            self.date_due = self.date_due or self.date_invoice
        else:
            pterm = self.payment_term_id
            pterm_list = pterm.\
                with_context(currency_id=self.company_id.currency_id.id,
                             partner_id=self.partner_id.
                             commercial_partner_id.id).\
                compute(value=1, date_ref=date_invoice)[0]
            self.date_due = max(line[0] for line in pterm_list)
