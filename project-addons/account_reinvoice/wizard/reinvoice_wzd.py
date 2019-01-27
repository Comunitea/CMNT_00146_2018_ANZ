
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
    def default_get(self, fields_list):
        res = super(ReinvoiceWzd, self).default_get(fields_list)
        print (self._context)
        active_id = self._context.get('active_id', False)
        if active_id:
            a_id = self.env['account.invoice'].browse(active_id)
            res['sale_type_id'] = a_id.associate_id.sale_type and a_id.associate_id.sale_type.id or False

        return res
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
            rule = self.env['reinvoice.rule'].get_reinvoice_discount(line, supplier)
            if not rule:
                inv_ass.message_post(body="No se ha encontrado una regla de descuento para %s"%line.display_name)

            line_vals = {
                'name': line.name + _(' (Reinvoice)'),
                'account_id': account_id,
                'invoice_line_tax_ids': [(6, 0, new_tax_ids)],
                'discount': rule and rule.customer_discount or 0.00,
            }
            line.write(line_vals)
        return True

    def get_invoices_values(self, inv):
        sale_type_id = inv.associate_id.sale_type or self.sale_type_id
        vals = {
                'partner_id': inv.associate_id.id,
                'origin': inv.number or inv.reference,
                'type':
                'out_invoice' if inv.type == 'in_invoice' else 'out_refund',
                'account_id': inv.associate_id.property_account_receivable_id.id,
                # 'reference': reference,
                # 'date_invoice': fields.Date.today(),,
                'user_id': self._uid,
                'name': inv.name,
                'from_supplier': True,
                'journal_id': sale_type_id.journal_id.id,
                'operating_unit_id': sale_type_id.operating_unit_id.id,
                'sale_type_id': sale_type_id.id,
                'date_value': inv.date_value,
                'payment_mode_id': inv.associate_id.customer_payment_mode_id.id,
                'payment_term_id': inv.associate_id.property_payment_term_id.id,
                'fiscal_position_id': inv.associate_id.property_account_position_id.id
                }
        return vals

    def get_invoices(self, invoices):
        created_invoices = self.env['account.invoice']

        for inv in invoices:

            if not inv.associate_id:
                raise UserError(
                    _('Invoice %s has not an associate.') % inv.number or inv.reference)

            copy_vals = self.get_invoices_values(inv)
            inv_ass = inv.copy(copy_vals)
            inv_ass.write({'supplier_invoice_id': inv.id})
            lineas = self._get_associated_invoice_lines(inv_ass, supplier=inv.partner_id)
            if not lineas:
                self.message_post(body="Error al crear las líneas de factura. Comprueba las reglas de refactura")
                inv_ass.unlink()
            else:
                created_invoices += inv_ass
                inv.write({'customer_invoice_id': inv_ass.id})
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
