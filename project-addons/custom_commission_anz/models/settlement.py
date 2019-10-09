# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SettlementLine(models.Model):
    _inherit = 'sale.commission.settlement.line'

    invoice = fields.Many2one(store=True)
    partner_id = fields.Many2one('res.partner', 
                                 related='invoice.partner_id', store=True)
    commission = fields.Many2one(store=True)


class Settlement(models.Model):
    _inherit = 'sale.commission.settlement'

    state = fields.Selection(selection_add=[('validated', 'Validated')])

    @api.multi
    def action_validate(self):
        self.write({'state': 'validated'})

    @api.multi
    def action_back(self):
        self.write({'state': 'settled'})
