# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('barcode_rule_id')
    def onchange_barcode_rule_id(self):
        self.generate_type = self.barcode_rule_id.generate_type
        self.product_variant_ids.write({'barcode_rule_id': self.barcode_rule_id.id,
                                        'generate_type': self.barcode_rule_id.generate_type})

