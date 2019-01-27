# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ReInvoiceRule(models.Model):

    _name = 'reinvoice.rule'

    @api.multi
    def name_get(self):
        res = []
        for rule in self:
            name = "Regla de {} para {}: {}".format(rule.supplier_id.name, rule.affiliate and "Asociado" or "No asociado", rule.partner_id and rule.partner_id.name or 'Sin cliente')
            if rule.order_type == 'apply_discount':
                name_2 = "Categoría: {} Descuento: {} -> {}".format(
                    rule.supplier_customer_ranking_id or rule.supplier_customer_ranking_id.name or "Sin categoría",
                    rule.supplier_discount, rule.customer_discount)

            else:
                name_2 = "Descuento: {} {}".format(rule.order_type)

            res.append((rule.id, "{} >> {}".format(name, name_2)))
        return res

    supplier_id = fields.Many2one('res.partner', 'Proveedor', domain=[('supplier', '=', True)], required=True)
    brand_id = fields.Many2one('product.brand', 'Marca')
    partner_id = fields.Many2one('res.partner', 'Cliente', domain=[('customer', '=', True)])
    #scheduled_sale = fields.Boolean('Scheduled sale', help="If checked, apply scheduled discount, else repos discount", default=False)
    supplier_discount = fields.Float('Descuento proveedor')
    customer_discount = fields.Float('Descuento cliente')
    affiliate = fields.Boolean('Asociado', default=True)
    supplier_customer_ranking_id = fields.Many2one('supplier.customer.ranking', string="Clasificación")
    order_type = fields.Selection([('all_discount', 'Mantener descuento'), ('0_discount', 'Descuento a 0'), ('apply_discount', 'Aplicar regla')],
                                  string="Tipo de regla",
                                  default='apply_discount',
                                  help="Mantener descuento: No aplica ninguna regla\n"
                                       "Descuento a 0: Aplica siempre 0%\n"
                                       "Aplicar regla: Aplica el descuento de la regla que se obtenga")

    def get_reinvoice_discount(self, line, supplier):

        partner_id = line.invoice_id.partner_id
        product_id = line.product_id


        domain = ['|', ('partner_id', '=', partner_id.id), ('partner_id', '=', False),
                  '|', ('brand_id', '=', product_id.product_brand_id.id), ('brand_id', '=', False),
                  '|', ('supplier_discount', '=', 0.00), ('supplier_discount', '=', line.discount),
                  ('affiliate', '=', partner_id.affiliate)]
        if supplier:
            domain += [('supplier_id', '=', supplier.id)]
            supplier_data = self.env['partner.supplier.data'].search(
                [('supplier_id', '=', supplier.id), ('customer_supplier_id', '=', line.invoice_id.associate_id.id)],
                limit=1)
            if supplier_data and supplier_data.supplier_customer_ranking_id:
                domain +=[('supplier_customer_ranking_id', '=', supplier_data.supplier_customer_ranking_id.id)]

        rule = self.search(domain, order='partner_id asc, brand_id asc, supplier_customer_ranking_id asc, supplier_discount desc', limit=1)
        print (rule)
        if not rule:
            raise UserError((
                                'No se ha encontrado una regla de refactura para este descuento {}, de este proveedor {}, y que {}sea asociado'.format(
                                    line.discount, supplier.display_name, 'no ' if partner_id.affiliate else '')))
        if rule.order_type == 'all_discount':
            return line.discount, False
        if rule.order_type == '0_discount':
            return 0, False

        return rule


