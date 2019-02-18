
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
        active_id = self._context.get('invoice_id', False) or self._context.get('active_id', False)
        if active_id:
            a_id = self.env['account.invoice'].browse(active_id)
            res['sale_type_id'] = a_id.associate_id.commercial_partner_id.sale_type and a_id.associate_id.commercial_partner_id.sale_type.id or False

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

    def _get_associated_invoice_lines(self, inv_ass, inv):
        # Get account
        cat = self.env['product.category'].search([], limit=1)
        account_id = cat.property_account_income_categ_id.id
        for line in inv_ass.invoice_line_ids:
            # Get new taxes
            # get new discount
            rule = self.env['reinvoice.rule'].get_reinvoice_rule(line, inv.partner_id)
            if rule:
                line.rule_id = rule
                price_unit = 0.00
                rule_discount = rule.get_customer_discount(line)

                if inv_ass.type in('out_invoice', 'out_refund'):
                    price_unit = rule.get_reinvoice_pvp(line.price_unit)
                ##
                line_vals = {
                    'name': line.name + _(' (Reinvoice)'),
                    'account_id': account_id,
                    'discount': rule_discount,
                    'pvp_supplier': line.price_unit,
                    'price_unit': price_unit,
                }
                line.write(line_vals)
                line.invoice_line_tax_ids = inv_ass.fiscal_position_id.map_tax(
                    line.product_id.taxes_id, line.product_id,
                    inv_ass.partner_id)
            else:
                return False
        return True

    def get_invoices_values(self, inv):
        sale_type_id = inv.associate_id.sale_type or self.sale_type_id
        txt_value_date = inv.import_txt_id and inv.import_txt_id.value_date or inv.value_date or inv.date_invoice
        vals = {
                'partner_id': inv.associate_id.id,
                'partner_shipping_id': inv.associate_shipping_id.id,
                'origin': inv.number or inv.reference,
                'type':
                'out_invoice' if inv.type == 'in_invoice' else 'out_refund',
                'account_id': inv.associate_id.commercial_partner_id.property_account_receivable_id.id,
                'user_id': self._uid,
                'name': inv.name,
                'from_supplier': True,
                'journal_id': sale_type_id.journal_id.id,
                'operating_unit_id': inv.operating_unit_id.id,
                'sale_type_id': sale_type_id.id,
                'payment_mode_id': inv.associate_id.commercial_partner_id.customer_payment_mode_id.id,
                'fiscal_position_id': inv.associate_id.commercial_partner_id.property_account_position_id.id,
                'customer_invoice_id': False,
                'value_date': txt_value_date,

                }
        return vals

    def get_invoices(self, invoices):
        created_invoices = self.env['account.invoice']
        inv_ids = invoices.filtered(lambda x: x.type in ('in_invoice', 'in_refund'))
        if not inv_ids:
             raise UserError('No hay ninguna factura para refacturar')
        for inv in inv_ids:
            if inv.customer_invoice_id:
                raise UserError(
                    _('Invoice %s has related customer invoice') % inv.number or inv.reference or inv.name)

            if not inv.associate_id:
                raise UserError(
                    _('Invoice %s has not an associate.') % inv.number or inv.reference)

            copy_vals = self.get_invoices_values(inv)
            inv_ass = inv.copy(copy_vals)
            inv_ass._onchange_partner_id()

            inv_ass.write({'supplier_invoice_id': inv.id,
                           'value_date': inv.value_date,
                           'customer_invoice_id': False
                           })
            lineas = self._get_associated_invoice_lines(inv_ass, inv)

            if not lineas:
                inv.message_post(body="Error al crear las líneas de factura. Comprueba las reglas de refactura")
                inv_ass.unlink()
            else:
                # Calculamos impuestos
                inv_ass.compute_taxes()
                created_invoices += inv_ass
                inv.write({'customer_invoice_id': inv_ass.id})
                inv_ass.check_payment_term()
                inv_ass.message_post(body="Esta factura ha sido creada desde el fichero: <a href=# data-oe-model=invoice.txt.import data-oe-id=%d>%s</a>"% (inv.id, inv.name))

        if not created_invoices:
            return False

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
