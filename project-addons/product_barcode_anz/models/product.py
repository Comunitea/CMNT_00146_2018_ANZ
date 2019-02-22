# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def generate_base(self):
        for variant in self.product_variant_ids.filtered(lambda x: not x.barcode_base):
            variant.generate_base()

    @api.multi
    def generate_barcode(self):
        self.ensure_one()
        for variant in self.product_variant_ids.filtered(lambda x: not x.barcode):
            variant.product_variant_ids.generate_barcode()

    @api.onchange('barcode_rule_id')
    def onchange_barcode_rule_id(self):
        self.product_variant_ids.write({'barcode_rule_id': self.barcode_rule_id.id})
        self.generate_type = self.barcode_rule_id.generate_type

