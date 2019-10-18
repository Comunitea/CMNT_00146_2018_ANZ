# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields



class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    auto_done = fields.Boolean('Auto done', help = 'Move done when is assigned')