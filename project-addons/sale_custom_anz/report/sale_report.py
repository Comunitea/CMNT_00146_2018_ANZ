# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Type', readonly=True)
    ref_change = fields.Boolean()

    def _select(self):
        return super(SaleReport, self)._select() + ", s.type_id as type_id, l.ref_change"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", s.type_id, l.ref_change"
