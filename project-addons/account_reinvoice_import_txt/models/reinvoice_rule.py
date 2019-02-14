# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression

class ReInvoiceRule(models.Model):

    _inherit = 'reinvoice.rule'


    def get_reinvoice_rule_for_txt(self, txt):
        shipping_id = txt.partner_shipping_id
        supplier_id = txt.partner_id

        domain =[('affiliate', '=', shipping_id.affiliate), ('supplier_id', '=', supplier_id.id)]

        supplier_data = self.env['partner.supplier.data'].search([('supplier_id', '=', supplier_id.id),
                                                                  ('customer_supplier_id', '=', shipping_id.id)], limit=1)
        if supplier_data:
            if supplier_data.supplier_customer_ranking_id:
                domain = expression.normalize_domain(domain)
                domain = expression.AND([domain, [('supplier_customer_ranking_id', '=', supplier_data.supplier_customer_ranking_id.id)]])
            domain = expression.normalize_domain(domain)
            domain = expression.AND([domain, ['|', ('partner_id', '=', txt.associate_id.id), ('partner_id', '=', False)]])

        discount_ids = txt.invoice_line_txt_import_ids.mapped('descuento')
        if discount_ids:
            domain = expression.normalize_domain(domain)
            domain = expression.AND(
                [domain, [('supplier_discount', 'in', tuple(discount_ids))]])
        rule_ids = self.search(domain, order='partner_id asc, brand_id asc, supplier_discount desc, customer_discount desc, order_type asc')
        return rule_ids
