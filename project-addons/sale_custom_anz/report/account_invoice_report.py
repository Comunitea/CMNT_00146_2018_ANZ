# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    ref_change = fields.Boolean()

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.ref_change"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", ail.ref_change"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ail.ref_change"
