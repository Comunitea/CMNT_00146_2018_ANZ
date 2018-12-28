# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    brand_ids = fields.Many2many('product.brand',
                                 "restrict_operating_unit_product_brand_rel",
                                 "unit_id",
                                 "brand_id",
                                 string="Brands",
                                 help="If empty, all brands")
    company_id = fields.Many2one("res.company", required=False)


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    def _check_company_operating_unit(self):
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_company_operating_unit(self):
        return True
