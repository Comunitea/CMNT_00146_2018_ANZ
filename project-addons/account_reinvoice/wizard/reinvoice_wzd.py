
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReinvoiceWzd(models.TransientModel):

    _name = 'reinvoice.wzd'

    group = fields.Boolean("Group by associate")
    sale_type_id = fields.Many2one('sale.order.type', "Sale type",
                                   required=True)

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

    def _get_associated_invoice_lines(self, inv_ass, supplier=False):
        # Get account
        cat = self.env['product.category'].search([], limit=1)
        account_id = cat.property_account_income_categ_id.id
        for line in inv_ass.invoice_line_ids:
            # Get new taxes
            new_tax_ids = self._get_purchase_tax(line.invoice_line_tax_ids)
            # get new discount
            new_discount = self.env['reinvoice.rule'].get_reinvoice_discount(line, supplier)
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
                    _('Invoice %s has not an associate.') % supp_origin)
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
                'journal_id': self.sale_type_id.journal_id.id,
                'operating_unit_id': self.sale_type_id.operating_unit_id.id,
                'sale_type_id': self.sale_type_id.id,
                'payment_mode_id': inv.associate_id.customer_payment_mode_id.id,
                'payment_term_id': inv.associate_id.property_payment_term_id.id,
            }
            inv_ass = inv.copy(copy_vals)
            inv.write({'customer_invoice_id': inv_ass.id})
            inv_ass.write({'supplier_invoice_id': inv.id})
            self._get_associated_invoice_lines(inv_ass, supplier=inv.partner_id)
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

        created_invoices = self.get_invoices(invoices)
        if created_invoices:
            return self.action_view_invoice(created_invoices)
