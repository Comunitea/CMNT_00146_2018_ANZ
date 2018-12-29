# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SettlementLine(models.Model):
    _inherit = 'sale.commission.settlement.line'

    invoice = fields.Many2one(store=True)
    commission = fields.Many2one(store=True)
