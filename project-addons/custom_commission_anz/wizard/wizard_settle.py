
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class SaleCommissionMakeSettle(models.TransientModel):

    _inherit = "sale.commission.make.settle"

    name = fields.Char('Settlements name', required=True)

    def _prepare_settlement_vals(self, agent, company, sett_from, sett_to):
        res = super(SaleCommissionMakeSettle, self)._prepare_settlement_vals(
            agent, company, sett_from, sett_to)
        res['name'] = self.name
        return res
