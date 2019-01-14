# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Type', readonly=True)
    ref_change = fields.Boolean()
    adidas_partner = fields.Many2one('res.partner', string='Delivery address', readonly=True)

    def _select(self):

        tiendas_propias = self.env['res.partner'].search([('ref', '=', 'OT2900000')])

        str = ", s.type_id as type_id, l.ref_change, " \
                                                   "case when ref_change then %s else s.partner_id end as adidas_partner "%(tiendas_propias and tiendas_propias.id or 1)

        return super(SaleReport, self)._select() + str


    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", s.type_id, l.ref_change, adidas_partner"
