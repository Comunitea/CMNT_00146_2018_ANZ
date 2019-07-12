# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
import datetime
import time

class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    rule_id = fields.Many2one('reinvoice.rule', string="Regla")


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    associate_shipping_id = fields.Many2one(
        'res.partner', 'Asociado / Externo', domain=[('customer', '=', True), ('external', '=', True)])
    associate_id = fields.Many2one(
        'res.partner', 'Asociado / Empresa', domain=[('customer', '=', True), ('company_type','=', 'company')])

    from_supplier = fields.Boolean('From supplier Invoice', copy=False,
                                   default=False)
    customer_invoice_id = fields.Many2one('account.invoice',
                                          'Customer Invoice', readonly=True,
                                           copy=False)
    supplier_invoice_id = fields.Many2one('account.invoice',
                                          'Supplier Invoice', readonly=True,
                                          copy=False)
    amount_discount = fields.Monetary(
        string='Amount discounted', store=False, readonly=True,
        compute='_compute_amount_discount')
    amount_year_discount = fields.Monetary(
        string='Discounted this year', store=False, readonly=True,
        compute='_compute_amount_year_discount')

    @api.onchange('associate_shipping_id')
    def associate_shipping_id_onchange(self):
        self.associate_id = self.associate_shipping_id.commercial_partner_id

    def get_invoice_sale_type(self):
        sale_type = self.associate_shipping_id.sale_type or self.associate_id.commercial_partner_id.sale_type or False
        return sale_type or False

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

    @api.multi
    def process_remap_taxes(self):
        for inv in self.filtered(lambda x: x.state == 'draft'):
            for line in inv.invoice_line_ids:
                txes_id = line.product_id.taxes_id if inv.type in ('out_invoice', 'out_refund') else line.product_id.supplier_taxes_id
                account_income_id = line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id
                account_expense_id = line.product_id.property_account_expense_id or line.product_id.categ_id.property_account_expense_categ_id
                line.account_id = account_income_id if inv.type in ('out_invoice', 'out_refund') else account_expense_id
                line.invoice_line_tax_ids = inv.fiscal_position_id.map_tax(txes_id, line.product_id, inv.partner_id)

    @api.multi
    def do_reinvoice(self):
        new_invoices = self.env['account.invoice']
        ctx = self._context.copy()
        for inv in self:
            sale_type = inv.get_invoice_sale_type()
            if sale_type:
                ctx.update(invoice_id=inv.id)
                wzd_id = self.with_context(ctx).env['reinvoice.wzd'].create({'sale_type_id': sale_type.id})
                new_invoice = wzd_id.get_invoices(inv)
                if new_invoice:
                    print("\n------------\nFACTURA DE ASOCIADO PARA : {}\n------------\n".format(
                        new_invoice.partner_id.name))
                    new_invoices += new_invoice

        return new_invoices

    @api.multi
    def unlink(self):
        inv_ass_ids = self.mapped('customer_invoice_id').filtered(lambda x:x.state=='draft')
        if inv_ass_ids:
            try:
                inv_ass_ids.unlink()
            except:
                pass
        res = super().unlink()

        return res