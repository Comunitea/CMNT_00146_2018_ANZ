# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


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
        string='Amount discounted', store=False, eadonly=True,
        compute='_compute_amount_discount')

    def _compute_amount_discount(self):
        for invoice in self:
            amount_discount = 0
            for line in invoice.invoice_line_ids:
                amount_discount += line.quantity * line.price_unit * \
                    (line.discount / 100.0)
            invoice.amount_discount = amount_discount
