# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class ProductSupplierTag(models.Model):
    _name = "product.supplier.tag"


    name = fields.Char('Name', required=1)
    partner_id = fields.Many2one('res.partner', domain = [('supplier', '=', True)], required=1)
    tag_id = fields.Many2one('product.tag', string="Local tag")


class ProductTag(models.Model):
    _inherit = 'product.tag'

    sup_tag_ids = fields.One2many('product.supplier.tag', 'tag_id', string="Sup. tag")

