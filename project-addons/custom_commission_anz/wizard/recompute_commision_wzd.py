
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class RecomputeCommissionWzd(models.TransientModel):

    _name = 'recompute.commission.wzd'

    @api.multi
    def recompute_commission(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.invoice'].browse(active_ids)
        if invoices:
            invoices.recompute_lines_agents()
        return
