# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

class StockLocation(models.Model):
    _inherit = "stock.location"

    icc_change = fields.Boolean('Icc', help='If checked, action assign will run under sudo and need orig moves')

    def should_bypass_reservation(self):
        self.ensure_one()
        if self.icc_change:
            return False
        return super().should_bypass_reservation()
