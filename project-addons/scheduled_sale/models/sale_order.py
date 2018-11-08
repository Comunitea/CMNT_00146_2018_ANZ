# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields
from odoo.osv import expression

class SaleOrder(models.Model):
    _inherit = "sale.order"

    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order', readonly=True)
    origin_scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order', readonly=True)

    @api.onchange('scheduled_sale_id')
    def scheduled_sale_id_change(self):

        if self.scheduled_sale_id:
            self.pricelist_id = self.scheduled_sale_id.pricelist_id
        else:
            self.onchange_partner_id()
            self.schedule_order=False



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')
    delivered_date = fields.Date("Delivered date")

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.schedule_order = self.product_id.schedule_product
            self.scheduled_sale_id = self.product_id.scheduled_sale_id
        return result

    @api.onchange('delivered_date')
    def onchange_delivered_date(self):
        self.delivered_date = "01-{}-{}".format(self.delivered_date.month, self.delivered_date.year)