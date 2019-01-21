# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ReInvoiceRule(models.Model):

    _name = 'reinvoice.rule'

    supplier_id = fields.Many2one('res.partner', 'Supplier', domain=[('supplier', '=', True)], required=True)
    brand_id = fields.Many2one('product.brand', 'Brand')
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)])
    scheduled_sale = fields.Boolean('Scheduled sale', help="If checked, apply scheduled discount, else repos discount", default=False)
    supplier_discount = fields.Float('Supplier Discount')
    customer_discount = fields.Float('Customer Discount')
    affiliate = fields.Boolean('Affiliate', default=False)
    supplier_customer_ranking_id = fields.Many2one('supplier.customer.ranking', string="Clasificación")




    def get_reinvoice_discount(self, line, supplier):
        partner_id = line.invoice_id.partner_id
        product_id = line.product_id
        supplier_data = self.env['partner.supplier.data'].search([('customer_supplier_id', '=', line.invoice_id.associate_id.id)], limit=1)
        scheduled_sale = product_id and product_id.scheduled_sale_id and True or False
        domain = ['|', ('partner_id', '=', partner_id.id), ('partner_id', '=', False),
                  '|', ('brand_id', '=', product_id.product_brand_id.id), ('brand_id', '=', False),
                  '|', ('supplier_discount', '=', 0.00), ('supplier_discount', '=', line.discount),
                  '|', ('supplier_customer_ranking_id', '=', supplier_data and supplier_data.supplier_customer_ranking_id.id or False), ('supplier_customer_ranking_id', '=', False),
                  ('supplier_id', '=', supplier.id),
                  ('scheduled_sale', '=', scheduled_sale),
                  ('affiliate', '=', partner_id.affiliate)
                  ]
        rule = self.search(domain, order='partner_id asc, brand_id asc, supplier_customer_ranking_id asc, supplier_discount desc')
        print (rule.mapped('customer_discount'))
        if not rule:
            print ('No encuentro regla')
            return line.discount
        res = rule[0]
        print ('Regla {} para {} :{} '.format(res.id, res.partner_id, res.customer_discount))
        return res.customer_discount