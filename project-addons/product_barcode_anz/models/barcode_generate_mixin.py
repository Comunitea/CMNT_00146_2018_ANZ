# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class BarcodeGenerateMixin(models.AbstractModel):
    _inherit = 'barcode.generate.mixin'

    @api.multi
    def generate_base(self):
        return super(BarcodeGenerateMixin, self.filtered(lambda x: not x.barcode)).generate_base()

    @api.multi
    def generate_barcode(self):
        return super(BarcodeGenerateMixin, self.filtered(lambda x: not x.barcode)).generate_barcode()
