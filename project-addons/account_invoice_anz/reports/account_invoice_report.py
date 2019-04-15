# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class AccountInvoiceReport(models.Model):

    _inherit = "account.invoice.report"

    discount = fields.Float(string='Discount', readonly=True)
    total_with_discount = fields.Float(string='With discount', readonly=True)
    average_discount = fields.Float(string='Avg. Discount', readonly=True, group_operator="avg")

    def _select(self):
        select_str = super(AccountInvoiceReport, self)._select()
        select_str += """
            , sub.discount
            , sub.total_with_discount as total_with_discount
            , sub.average_discount as average_discount
        """
        return select_str

    def _sub_select(self):
        select_str = super(AccountInvoiceReport, self)._sub_select()
        select_str += """
            , ail.discount * invoice_type.sign as discount
            , (ail.price_subtotal_signed + ail.discount) as total_with_discount
            ,
                case when (ail.price_subtotal_signed = 0 or (ail.price_subtotal_signed + ail.discount) = 0) then 100
                else (ail.discount / (ail.price_subtotal_signed + ail.discount)) * 100
                end
                as average_discount

        """
        return select_str
