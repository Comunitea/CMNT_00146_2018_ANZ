# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
import datetime
import time


import os


class PaymentTermBrandName(models.Model):
    _name = "payment.term.brand.name"

    payment_term_id = fields.Many2one('account.payment.term', string="Modo de pago")
    name = fields.Char('Nombre en proveedor')
    supplier_id = fields.Many2one('res.partner', "Proveedor", domain = [('supplier', '=', True)])

class AccountPaymentTerm(models.Model):

    _inherit = 'account.payment.term'
    brand_name_ids = fields.One2many('payment.term.brand.name', 'payment_term_id', string="Nombres en proveedores")


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    date_invoice_from_associate_order = fields.Date(string='Due Date',
         readonly=True, states={'draft': [('readonly', False)]},
         help="Imported form txt import")
    import_txt_id = fields.Many2one('invoice.txt.import', string="Importado desde ")


    def check_existing_txt(self):
        self.env['invoice.txt.import'].import_txt_invoice()
