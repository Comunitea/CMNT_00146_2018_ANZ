# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    type = fields.Selection(related='invoice_id.type')

