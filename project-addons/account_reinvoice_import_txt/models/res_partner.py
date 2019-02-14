# -*- coding: utf-8 -*-
# © 2018 Comunitea Servicios Tecnologicos (<http://www.comunitea.com>)
# Kiko Sanchez (<kiko@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, tools, api, _

class SupplierCodeTxtImport(models.Model):

    _name = "supplier.code.txt.import"

    supplier_id = fields.Many2one('res.partner', string="Proveedor", domain =[('supplier','=', True)], required=1)
    customer_id = fields.Many2one('res.partner', string="Cliente", domain =[('customer','=', True)], required=1)
    code = fields.Char('Codigo del cliente en el proveedor', required=1)
    name = fields.Char('Nombre del cliente en el proveedor')

    def create(self, vals):
        if not vals.get('name', False):
            supplier_id = self.env['res.partner'].browse(vals['supplier_id']).name
            customer_id = self.env['res.partner'].browse(vals['customer_id']).name
            vals['name'] = "{} -> {}".format(supplier_id, customer_id)
        return super(SupplierCodeTxtImport, self).create(vals)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    supplier_code_ids = fields.One2many('supplier.code.txt.import', 'customer_id', string="Codigo en clientes")
    customer_code_ids = fields.One2many('supplier.code.txt.import', 'supplier_id', string="Codigo en proveedores")

    external = fields.Boolean('Externo')

    supplier_id = fields.Many2one('res.partner', 'Proveedor', domain="[('supplier', '=', True)]")
    supplier_code = fields.Char("Código externo")
    supplier_str = fields.Char("Nombre en factura")
    supplier_customer_ranking_id = fields.Many2one('supplier.customer.ranking', string="Clasificación")

