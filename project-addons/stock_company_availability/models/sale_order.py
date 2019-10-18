# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for order in self:
            order.sudo().mapped('picking_ids').filtered(lambda x: x.company_id != order.company_id).action_cancel()
        return res