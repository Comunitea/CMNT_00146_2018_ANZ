# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
import datetime
import time


import os
from odoo.tools import float_is_zero

class PaymentTermBrandName(models.Model):
    _name = "payment.term.brand.name"

    payment_term_id = fields.Many2one('account.payment.term', string="Modo de pago")
    name = fields.Char('Nombre en proveedor')
    supplier_id = fields.Many2one('res.partner', "Proveedor", domain = [('supplier', '=', True)])

class AccountPaymentTerm(models.Model):

    _inherit = 'account.payment.term'
    brand_name_ids = fields.One2many('payment.term.brand.name', 'payment_term_id', string="Nombres en proveedores")


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    import_txt_id = fields.Many2one('invoice.txt.import', string="Importado desde ", copy=False)
    payment_day_ids = fields.One2many(related="import_txt_id.payment_day_ids")

    @api.onchange('payment_term_id', 'date_invoice', 'value_date')
    def _onchange_payment_term_date_invoice(self):

        ctx = self._context.copy()
        ctx.update(invoice_id=self.id)
        return super(AccountInvoice, self.with_context(ctx))._onchange_payment_term_date_invoice()

    def _compute_amount(self):
        for line in self:
            if not(line.import_txt_id and line.env['ir.config_parameter'].sudo().get_param(
                'import_account.overwrite_odoo_amount', 'False').lower() == 'true'):
                return super()._compute_amount()

            round_curr = line.currency_id.round
            line.amount_untaxed = line.import_txt_id.valor_neto
            line.amount_tax = line.import_txt_id.total_amount - line.import_txt_id.valor_neto
            line.amount_total = line.import_txt_id.total_amount
            amount_total_company_signed = line.amount_total
            amount_untaxed_signed = line.amount_untaxed
            if line.currency_id and line.company_id and line.currency_id != line.company_id.currency_id:
                currency_id = line.currency_id.with_context(date=line.date_value or line.date_invoice)
                amount_total_company_signed = currency_id.compute(line.amount_total, line.company_id.currency_id)
                amount_untaxed_signed = currency_id.compute(line.amount_untaxed, line.company_id.currency_id)
            sign = line.type in ['in_refund', 'out_refund'] and -1 or 1
            line.amount_total_company_signed = amount_total_company_signed * sign
            line.amount_total_signed = line.amount_total * sign
            line.amount_untaxed_signed = amount_untaxed_signed * sign

class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    pvp_supplier = fields.Monetary(string='Precio importado', copy=False)
    imported_price_subtotal = fields.Monetary(string='Total importado', copy=False)


    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):

        if not(self.invoice_id.import_txt_id and self.env['ir.config_parameter'].sudo().get_param(
            'import_account.overwrite_odoo_amount', 'False').lower() == 'true'):
            return super()._compute_price()

        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)

        self.price_subtotal = self.imported_price_subtotal
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1

        self.price_subtotal_signed = self.price_subtotal * sign
        price_subtotal_signed = self.invoice_id.currency_id.with_context(
            date=self.invoice_id._get_currency_rate_date()).compute(self.price_subtotal,
                                                                    self.invoice_id.company_id.currency_id)
        self.price_subtotal_signed = price_subtotal_signed * sign


class AccountPaymentTerm(models.Model):

    _inherit = "account.payment.term"

    @api.multi
    def compute(self, value, date_ref=False):
        invoice = self.env['account.invoice'].browse(self._context.get('invoice_id', False))
        self.ensure_one()


        if not invoice or not invoice.payment_day_ids or invoice.type not in ('in_invoice', 'in_refund'):
            original = super(AccountPaymentTerm, self).compute(value, date_ref)
            print ("-----ORIGINAL--------")
            return original

        res = []
        last_amount = invoice.amount_total
        prec = invoice.currency_id.decimal_places
        for pay in invoice.payment_day_ids:
            last_amount -= pay.amount
            res.append((pay.date, -pay.amount))
        if not float_is_zero(last_amount, 4):
            res[-1] = (res[-1][0], invoice.currency_id.round(-last_amount + res[-1][1]))
        return [res]
