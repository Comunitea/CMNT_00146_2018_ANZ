# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models, fields


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    brand_ids = fields.Many2many('product.brand',
                                                  "restrict_operating_unit_product_brand_rel",
                                                  "unit_id",
                                                  "brand_id",
                                                  string="Brands",
                                                  help="If empty, all brands"
                                                  )

