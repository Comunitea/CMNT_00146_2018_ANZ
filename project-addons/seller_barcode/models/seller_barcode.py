# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.addons import decimal_precision as dp



class ProductImage(models.Model):
    _inherit = 'product.image'
    barcode_template_id = fields.Many2one ('seller.barcode.template', 'Related barcode template', copy=True)

class BarcodeTag(models.Model):
    _name = 'barcode.tag'

    name = fields.Char('Barcode tag name')
    tag_id = fields.Many2one('product.tag')

class ProductTag(models.Model):
    _inherit = "product.tag"

    barcode_tag_ids = fields.One2many('barcode.tag', 'tag_id')

class ProductBarcodeAge(models.Model):
    _name = 'product.barcode.age'
    _order = 'name asc, code asc'

    name = fields.Char('Barcode age group')
    code = fields.Char('Age code')
    brand_id = fields.Many2one('product.brand', 'Marca')

class ProductBarcodeGender(models.Model):
    _name = 'product.barcode.gender'
    _order = 'name asc, code asc'

    name = fields.Char('Barcode gender group')
    code = fields.Char('Gender code')
    brand_id = fields.Many2one('product.brand', 'Marca')

class SellerBarcodeTemplate(models.Model):
    _name = "seller.barcode.template"

    name = fields.Char('Name')
    template = fields.Char('Template name')
    ref = fields.Char('Internal ref')
    active = fields.Boolean('Active', default=True)
    description = fields.Char('Description')
    arancel = fields.Char('Arancel')

    brand = fields.Char('Brand', required=1)
    brand_id = fields.Many2one('product.brand')

    category = fields.Char('Category')
    category_id = fields.Many2one('product.category')

    partner = fields.Char('Seller name')
    color = fields.Char('Color')
    attribute_name = fields.Char('Size type', help="Attribute name")

    cost = fields.Float('Cost', digits=dp.get_precision('Product Price'))
    pvp = fields.Float('PVP', digits=dp.get_precision('Product Price'))

    partner_id = fields.Many2one('res.partner', 'Seller', domain= [('seller', '=', True)])
    image = fields.Char('Image name')
    barcode_ids = fields.One2many('seller.barcode', 'template_id', string='Barcodes')
    ##CATEG FIELDS
    tag = fields.Char('Tags', help="Tags separated by coma")
    tag_ids = fields.Many2many(string='Tags',
                               comodel_name='product.tag',
                               relation='barcode_template__product_tag_rel',
                               column1='tag_id',
                               column2='seller_barcode_id')
    color_id = fields.Many2one('product.attribute.value', domain=[('is_color', '=', True)])
    attribute_id = fields.Many2one('product.attribute')
    age = fields.Many2one('product.barcode.age')
    gender = fields.Many2one('product.barcode.gender')
    ## WEB FIELDS
    image_ids = fields.One2many('product.image', 'barcode_template_id', 'Images')
    web_header = fields.Html('Web header')
    web_body = fields.Html('Web header')
    web_footer = fields.Html('Web header')

class SellerBarcode(models.Model):

    _name = "seller.barcode"

    barcode = fields.Char('Barcode', required=1)
    ref = fields.Char('Internal ref', help = 'Variant ref , if diferent from template')

    barcode_name = fields.Char('Name', help='Variant name , if diferent from template')
    template_id = fields.Many2one('seller.barcode.template')

    attribute_value_name = fields.Char('Size name', help="Attribute value name")
    attribute_value_id = fields.Many2one('product.attribute.value')
    attribute_value_code = fields.Char(related='attribute_value_id.supplier_code')
