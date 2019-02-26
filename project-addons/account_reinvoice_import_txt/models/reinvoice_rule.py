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
        domain_data = [('supplier_id', '=', supplier_id.id), '|', ('supplier_code', '=', shipping_id.supplier_code),
                       ('supplier_str', '=', shipping_id.supplier_str)]
        supplier_data = self.env['res.partner'].search(domain_data, limit=1)
        if supplier_data:
            if supplier_data.supplier_customer_ranking_id:
                domain = expression.normalize_domain(domain)
                domain = expression.AND(
                    [domain, [('supplier_customer_ranking_id', '=', supplier_data.supplier_customer_ranking_id.id)]])
            domain = expression.normalize_domain(domain)
            domain = expression.AND([domain, ['|', ('partner_id', '=', shipping_id.id), ('partner_id', '=', False)]])
        else:
            domain = expression.normalize_domain(domain)
            domain = expression.AND([domain, [('partner_id', '=', False)]])

        rule_ids = self.search(domain, order='partner_id asc, brand_id asc, supplier_discount desc, customer_discount desc, order_type asc')
        discount_ids = txt.invoice_line_txt_import_ids.mapped('descuento')
        rule_ids = rule_ids.filtered(lambda x:x.supplier_discount in discount_ids)
        print ("{} {}".format(domain, rule_ids))
        return rule_ids
