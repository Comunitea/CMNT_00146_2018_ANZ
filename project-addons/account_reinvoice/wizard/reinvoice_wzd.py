
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReinvoiceWzd(models.TransientModel):

    _name = 'reinvoice.wzd'

    group = fields.Boolean("Group by associate")

    # @api.model
    # def _get_invoice_vals(self, invoices):
    #     inv = invoices[0]
    #     vals = {
    #         'partner_id': inv.associate_id.id,
    #         'name': '/',
    #         'origin': ','.join([x.name or '' for x in invoices]),
    #         'type':
    #         'out_invoice' if inv.type == 'in_invoice' else 'out_refund',
    #         'account_id': inv.associate_id.property_account_receivable_id.id,
    #         # 'reference': reference,
    #         'date_invoice': fields.Date.today(),
    #         'user_id': self._uid,
    #         'from_supplier': True,
    #     }
    #     return vals

    # @api.model
    # def _get_purchase_tax(self, tax):
    #     tax_ids = []
    #     domain = [
    #         ('type_tax_use', '=', 'sale'),
    #         ('amount', '=', tax.amount)
    #     ]
    #     taxes = self.env['account.tax'].search(domain, limit=1)
    #     if taxes:
    #         tax_ids = taxes.ids
    #     return tax_ids

    # @api.model
    # def _get_line_vals(self, inv, invoices):
    #     res = []
    #     group_line_tax = {}
    #     # Group by tax
    #     for line in invoices.mapped('invoice_line_ids'):
    #         tax = line.invoice_line_tax_ids and \
    #             line.invoice_line_tax_ids[0] or False

    #         if tax not in group_line_tax:
    #             group_line_tax[tax] = 0.0
    #         group_line_tax[tax] += line.price_unit
    #     # Get account
    #     cat = self.env['product.category'].search([], limit=1)
    #     account_id = cat.property_account_income_categ_id.id

    #     # Create a line for each diferent tax
    #     for tax in group_line_tax:
    #         tax_ids = self._get_purchase_tax(tax)
    #         price_unit = group_line_tax[tax]
    #         line_vals = {
    #             'name': _('From Supplier Import'),
    #             'quantity': 1.0,
    #             'price_unit': price_unit,
    #             'account_id': account_id,
    #             'invoice_id': inv.id,
    #             'invoice_line_tax_ids': [(6, 0, tax_ids)]
    #         }
    #         res.append((0, 0, line_vals))
    #     return res

    # def get_invoices_grouped(self, invoices):
    #     created_invoices = self.env['account.invoice']
    #     # Group by associate_id
    #     inv_grouped = {}
    #     for inv in invoices:
    #         if not inv.associate_id:
    #             continue
    #         if inv.associate_id.id not in inv_grouped:
    #             inv_grouped[inv.associate_id.id] = self.env['account.invoice']
    #         inv_grouped[inv.associate_id.id] += inv

    #     for associate_id in inv_grouped:
    #         # Create Invoice for each associate
    #         invoice_objs = inv_grouped[associate_id]
    #         vals = self._get_invoice_vals(invoice_objs)
    #         inv = self.env['account.invoice'].create(vals)

    #         created_invoices += inv
    #         # Write link between supplier and created invoice
    #         invoice_objs.write({'customer_invoice_id': inv.id})
    #         # Create lines
    #         line_vals = self._get_line_vals(inv, invoice_objs)
    #         if line_vals:
    #             inv.write({'invoice_line_ids': line_vals})
    #     return created_invoices

    @api.model
    def _get_purchase_tax(self, tax_objs):
        tax_ids = []
        for tax in tax_objs:
            domain = [
                ('type_tax_use', '=', 'sale'),
                ('amount', '=', tax.amount)
            ]
            taxes = self.env['account.tax'].search(domain, limit=1)
            if taxes:
                tax_ids.append(taxes.id)
        return tax_ids

    def _get_associated_invoice_lines(self, inv_ass):
        # Get account
        cat = self.env['product.category'].search([], limit=1)
        account_id = cat.property_account_income_categ_id.id
        for line in inv_ass.invoice_line_ids:
            # Get new taxes
            new_tax_ids = self._get_purchase_tax(line.invoice_line_tax_ids)
            # get new discount
            new_discount = line.discount
            if line.product_id.product_brand_id:
                new_discount = line.product_id.product_brand_id.\
                get_reinvoice_discount(line)
            line_vals = {
                'name': line.name + _(' (Reinvoice)'),
                'account_id': account_id,
                'invoice_line_tax_ids': [(6, 0, new_tax_ids)],
                'discount': new_discount
            }
            line.write(line_vals)

    def get_invoices(self, invoices):
        created_invoices = self.env['account.invoice']
        for inv in invoices:
            supp_origin = inv.number or inv.reference
            if not inv.associate_id:
                raise UserError(
                    _('Invoice %s has not an associate.') & supp_origin)
            copy_vals = {
                'partner_id': inv.associate_id.id,
                # 'name': '/',
                'origin': supp_origin,
                'type':
                'out_invoice' if inv.type == 'in_invoice' else 'out_refund',
                'account_id': inv.associate_id.
                property_account_receivable_id.id,
                # 'reference': reference,
                # 'date_invoice': fields.Date.today(),
                'user_id': self._uid,
                'from_supplier': True,
            }
            inv_ass = inv.copy(copy_vals)
            inv.write({'customer_invoice_id': inv_ass.id})
            inv_ass.write({'supplier_invoice_id': inv.id})
            self._get_associated_invoice_lines(inv_ass)
            created_invoices += inv_ass
        return created_invoices

    @api.multi
    def action_view_invoice(self, invoices):
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id,
                               'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def create_invoices(self):
        self.ensure_one()
        invoices = self.env['account.invoice'].\
            browse(self._context.get('active_ids', []))

        # created_invoices = self.env['account.invoice']
        # if self.group:
        #     created_invoices = self.get_invoices_grouped(invoices)
        # else:
        #     created_invoices = self.get_invoices(invoices)

        created_invoices = self.get_invoices(invoices)
        if created_invoices:
            return self.action_view_invoice(created_invoices)
