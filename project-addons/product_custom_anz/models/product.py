# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models

class ProductAttributeCategory(models.Model):
    _name = 'product.attribute.category'

    name = fields.Char(string='Category')

class ProductAttribute(models.Model):

    _inherit = "product.attribute"

    is_color = fields.Boolean("Is color",
                              help="Check it if attribute will contain colors")
    is_tboot = fields.Boolean("Is type of boot",
                              help="Check it if attribute will contain \
                              type of boots")

    product_brand_id = fields.Many2one('product.brand', 'Brand')
    attribute_category_id = fields.Many2one('product.category', 'Category')


class ProductAttributeValue(models.Model):

    _inherit = "product.attribute.value"

    is_color = fields.Boolean("Is color",
                              related="attribute_id.is_color",
                              readonly=True)
    is_tboot = fields.Boolean("Is type of boot",
                              related="attribute_id.is_tboot",
                              readonly=True)

    supplier_code = fields.Char("Supplier name")