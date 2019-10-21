# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _prepare_agents_vals(self):
        self.ensure_one()
        super()._prepare_agents_vals()
        return self._prepare_agents_vals_by_brand(
            self.invoice_id.partner_id, self.product_id,
            self.invoice_id.user_id.id, self.discount
        )

    @api.model
    def create(self, vals):
        product_id = vals.get('product_id', False)
        invoice_id = vals.get('invoice_id', False)
        if invoice_id and product_id:
            invoice = self.env['account.invoice'].browse(invoice_id)
            partner = invoice.partner_id
            product = self.env['product.product'].browse(product_id)
            agent_vals = self._prepare_agents_vals_by_brand(
                partner, product, invoice.user_id.id, 
                vals.get('discount', 0.0))
            vals['agents'] = agent_vals
        return super().create(vals)

    @api.multi
    def write(self, vals):
        self2 = self.env['account.invoice.line']
        if vals.get('product_id') or 'discount' in vals:
            for line in self:
                if (vals.get('product_id') and
                        line.product_id.id != vals['product_id']) or \
                        vals.get('discount') and \
                        line.discount != vals['discount']:
                    self2 += line
        res = super().write(vals)
        if self2:
            self2.recompute_agents()
        return res


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    reinvoice_commercial = fields.Many2one('res.users', 'Reinvoice commercial')

    @api.multi
    def do_reinvoice(self):
        """
        Recalculo de comisiones cuando se importan por texto
        """
        invoices = super().do_reinvoice()
        if invoices:
            invoices.recompute_lines_agents()
        return invoices

    @api.multi
    def write(self, vals):
        """
        Recalcular comisiones cuando se cambia el comercial
        """
        res = super().write(vals)
        if 'user_id' in vals:
            self.invoice_line_ids.recompute_agents()
        return res


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    date_due = fields.Date(
        string="Invoice date",
        related="invoice.date_due",
        store=True,
        readonly=True,
    )
