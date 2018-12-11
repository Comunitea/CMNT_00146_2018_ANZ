# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

#from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    deliver_month = fields.Char('Requested month', readonly=1)

    def _select(self):
        return super(SaleReport, self)._select() + ",l.deliver_month as deliver_month "

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ",l.deliver_month "

