# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('invoice_line_ids')
    def _compute_account_invoice_line_count(self):
        for invoice in self:
            invoice.account_invoice_line_template_count = len(
                invoice.template_lines)

    account_invoice_line_template_count = fields.Integer(
        'Template line count', compute='_compute_account_invoice_line_count')
    template_lines = fields.One2many('account.invoice.line.template',
                                     'invoice_id')

    def action_view_invoice_lines_template_group(self):
        action = self.env.ref(
            'account_invoice_line_template.action_account_invoice_line_template').read()[0]
        action['domain'] = [('invoice_id', '=', self.id)]
        return action


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    product_tmpl_id = fields.Many2one(
        'product.template', string="Template")

    @api.multi
    def write(self, vals):
        if 'product_tmpl_id' not in vals and vals.get('product_id', False):
            tmpl_id = self.env['product.product']. \
                search_read([('id', '=', vals['product_id'])], ['product_tmpl_id'])
            vals.update({'product_tmpl_id': tmpl_id and tmpl_id[0]['product_tmpl_id'][0]})
        return super(AccountInvoiceLine, self).write(vals)

    @api.model
    def create(self, vals):
        if 'product_tmpl_id' not in vals and vals.get('product_id', False):
            tmpl_id = self.env['product.product']. \
                search_read([('id', '=', vals['product_id'])], ['product_tmpl_id'])
            vals.update({'product_tmpl_id': tmpl_id and tmpl_id[0]['product_tmpl_id'][0]})
        return super(AccountInvoiceLine, self).create(vals)

