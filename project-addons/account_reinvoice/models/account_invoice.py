# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models
import datetime
import time


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    associate_id = fields.Many2one(
        'res.partner', 'Associate',
        domain=[('customer', '=', True)]
    )
    from_supplier = fields.Boolean('From supplier Invoice')
    customer_invoice_id = fields.Many2one('account.invoice',
                                          'Customer Invoice', readonly=True)
    supplier_invoice_id = fields.Many2one('account.invoice',
                                          'Supplier Invoice', readonly=True)
    amount_discount = fields.Monetary(
        string='Amount discounted', store=False, readonly=True,
        compute='_compute_amount_discount')
    amount_year_discount = fields.Monetary(
        string='Discounted this year', store=False, readonly=True,
        compute='_compute_amount_year_discount')

    def _compute_amount_discount(self):
        for invoice in self:
            amount_discount = 0
            for line in invoice.invoice_line_ids:
                amount_discount += line.quantity * line.price_unit * \
                    (line.discount / 100.0)
            invoice.amount_discount = amount_discount

    def _compute_amount_year_discount(self):
        now = datetime.datetime.now()
        current_year = now.year
        start_date = str(current_year) + '-' + '01' + '-' + '01'
        end_date = str(current_year) + '-' + '12' + '-' + '31'
        for invoice in self:
            domain = [
                ('state', 'not in', ['draft', 'cancel']),
                ('date_invoice', '>=', start_date),
                ('date_invoice', '<=', end_date),
                ('commercial_partner_id', '=',
                 invoice.commercial_partner_id.id)
            ]
            invoices = self.search(domain)
            invoice.amount_year_discount = \
                sum([x.amount_discount for x in invoices])
