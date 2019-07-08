
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class ReinvoiceWzd(models.TransientModel):

    _inherit = 'reinvoice.wzd'

    @api.multi
    def get_invoices(self, invoices):
        created_invoices = super().get_invoices(invoices)
        if created_invoices:
            created_invoices.recompute_lines_agents()
        return created_invoices
