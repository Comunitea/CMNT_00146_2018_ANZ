# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
class ReInvoiceRule(models.Model):

    _name = 'reinvoice.rule'
    _order = 'partner_id asc, brand_id asc, supplier_discount desc, customer_discount desc, order_type asc, affiliate, supplier_customer_ranking_id'

    @api.multi
    def name_get(self):
        res = []
        for rule in self:
            name = "Regla de {} para {}: {}".format(rule.supplier_id.name, rule.affiliate and "Asociado" or "No asociado", rule.partner_id and rule.partner_id.name or 'Sin cliente')
            if rule.order_type == '0_apply_discount':
                name_2 = "Categoría: {} Descuento: {} -> {}".format(
                    rule.supplier_customer_ranking_id or rule.supplier_customer_ranking_id.name or "Sin categoría",
                    rule.supplier_discount, rule.customer_discount)

            else:
                name_2 = "Descuento: {}".format(rule.order_type)

            res.append((rule.id, "{} >> {}".format(name, name_2)))
        return res

    supplier_id = fields.Many2one('res.partner', 'Proveedor', domain=[('supplier', '=', True)], required=True)
    brand_id = fields.Many2one('product.brand', 'Marca')
    partner_id = fields.Many2one('res.partner', 'Cliente', domain=[('customer', '=', True)])
    #scheduled_sale = fields.Boolean('Scheduled sale', help="If checked, apply scheduled discount, else repos discount", default=False)
    supplier_discount = fields.Float('Descuento proveedor')
    customer_discount = fields.Float('Descuento cliente')
    customer_charge = fields.Float('Recargo en cliente', default = 0)


    affiliate = fields.Boolean('Asociado', default=True)
    supplier_customer_ranking_id = fields.Many2one('supplier.customer.ranking', string="Clasificación")
    order_type = fields.Selection([('2_all_discount', 'Mantener descuento'), ('1_0_discount', 'Descuento a 0'), ('0_apply_discount', 'Aplicar regla')],
                                  string="Tipo de regla",
                                  default='0_apply_discount',
                                  help="Mantener descuento: No aplica ninguna regla\n"
                                       "Descuento a 0: Aplica siempre 0%\n"
                                       "Aplicar regla: Aplica el descuento de la regla que se obtenga")



    def get_reinvoice_pvp(self, price_unit):
        if self.customer_charge != 0.00:
            return price_unit * (1 + self.customer_charge/100)
        return price_unit

    def get_customer_discount(self, line):
        if self.order_type == '2_all_discount':
            rule_discount = line.discount
        elif self.order_type == '1_0_discount':
            rule_discount = 0.00
        else:
            rule_discount = self.customer_discount
        return rule_discount


    def get_reinvoice_rule(self, line, supplier):
        partner_id = line.invoice_id.partner_id
        product_id = line.product_id
        domain = [('affiliate', '=', partner_id.affiliate)]
        if supplier:
            domain = expression.AND([domain, [('supplier_id', '=', supplier.id)] ])

            supplier_data = self.env['partner.supplier.data'].search(
                [('supplier_id', '=', supplier.id), ('customer_supplier_id', '=', line.invoice_id.associate_id.id)],
                limit=1)
            if supplier_data:
                if supplier_data.supplier_customer_ranking_id:
                    domain = expression.AND([domain, [('supplier_customer_ranking_id', '=', supplier_data.supplier_customer_ranking_id.id)]])

                domain = expression.normalize_domain(domain)
                domain = expression.AND([domain, ['|', ('partner_id', '=', line.invoice_id.associate_id.id), ('partner_id', '=', False)]])

        if product_id.product_brand_id:
            domain = expression.normalize_domain(domain)
            domain = expression.AND([domain, ['|', ('brand_id', '=', product_id.product_brand_id.id), ('brand_id', '=', False)]])

        domain = expression.normalize_domain(domain)
        domain = expression.AND([domain, ['|', ('supplier_discount', '=', 0.00), ('supplier_discount', '=', line.discount)]])
        rule = self.search(domain, order='partner_id asc, brand_id asc, supplier_discount desc, customer_discount desc, order_type asc')

        if not rule:
            message = ('No se ha encontrado una regla de refactura para: Descuento: {}, Proveedor: {}, {} Asociado'.format(
                                    line.discount, supplier.display_name, 'no ' if not partner_id.affiliate else ''))
            if product_id.product_brand_id:
                message = '{}, Marca: {}'.format(message, product_id.product_brand_id.name)

            if supplier_data and supplier_data.supplier_customer_ranking_id:
                message = '{}, Clasificación: {}'.format(message, supplier_data.supplier_customer_ranking_id.name)

            raise UserError(message)

        rule = rule[0]
        return rule


