# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

#from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"


    type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Type', readonly=True)

    def _select(self):
        return super(SaleReport, self)._select() + ", s.type_id as type_id"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", s.type_id "

