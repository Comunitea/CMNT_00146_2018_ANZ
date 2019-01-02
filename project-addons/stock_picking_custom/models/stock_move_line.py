# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _order = "barcode asc, barcode_dest asc, result_package_id desc, id"

    barcode = fields.Char(related='location_id.barcode', store=True)
    barcode_dest = fields.Char(related='location_dest_id.barcode', store=True)

