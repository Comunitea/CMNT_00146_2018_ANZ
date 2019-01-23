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

    def check_existing_txt(self):
        self.env['invoice.txt.import'].import_txt_invoice()
