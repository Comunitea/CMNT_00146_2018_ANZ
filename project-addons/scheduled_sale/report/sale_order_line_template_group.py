# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class SaleOrderLineTemplateGroup(models.Model):

    _inherit = "sale.order.line.template.group"

    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order', readonly=1)
    deliver_month = fields.Char('Requested month', help="Date format = day/month/year(2 digits)", readonly=1)

    def _select(self):
        return super(SaleOrderLineTemplateGroup, self)._select() + ', l.deliver_month as deliver_month, s.scheduled_sale_id as scheduled_sale_id '

    def _group_by(self):
        return super(SaleOrderLineTemplateGroup, self)._group_by() + ', l.deliver_month, s.scheduled_sale_id '