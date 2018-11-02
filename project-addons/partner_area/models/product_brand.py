# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductBrand(models.Model):

    _inherit = 'product.brand'

    allowed_area_ids = fields.Many2many('res.partner.area',
                                        "allowed_product_brand_partner_area_rel",
                                        "brand_id",
                                        "area_id", string="Allowed areas", help="If empty, all areas; else allowed only in this areas")
    restricted_area_ids = fields.Many2many('res.partner.area',
                                        "restrict_product_brand_partner_area_rel",
                                        "brand_id",
                                        "area_id", string="Restricted areas", help="Restricted areas")

    allowed_area_ids_count = fields.Integer(
        string='Allowed areas',
        compute='_get_area_ids_count',
    )
    restricted_area_ids_count = fields.Integer(
        string='Allowed areas',
        compute='_get_area_ids_count',
    )

    @api.multi
    @api.depends('product_ids')
    def _get_area_ids_count(self):
        for brand in self:
            brand.allowed_area_ids_count = len(brand.allowed_area_ids)
            brand.restricted_area_ids_count = len(brand.restricted_area_ids)

