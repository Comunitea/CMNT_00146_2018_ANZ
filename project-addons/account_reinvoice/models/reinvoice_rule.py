# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ReInvoiceRule(models.Model):

    _name = 'reinvoice.rule'

    brand_id = fields.Many2one('product.brand', 'Brand', required=True)
    partner_id = fields.Many2one('res.partner', 'Customer')
    supplier_discount = fields.Float('Supplier Discount')
    customer_discount = fields.Float('Customer Discount')
