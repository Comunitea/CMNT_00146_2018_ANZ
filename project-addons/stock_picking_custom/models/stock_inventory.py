# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class StockInventoryLine(models.Model):

    _inherit = "stock.inventory.line"

    def _get_quants(self):

        return super()._get_quants()
        ## Ya no hará falta después de la modificación
        return self.env['stock.quant'].search([
            '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False),
            ('location_id', '=', self.location_id.id),
            ('lot_id', '=', self.prod_lot_id.id),
            ('product_id', '=', self.product_id.id),
            ('owner_id', '=', self.partner_id.id),
            ('package_id', '=', self.package_id.id)])
