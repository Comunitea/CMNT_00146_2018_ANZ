# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields

class StockPicking(models.Model):
    _inherit = "stock.picking"

    deliver_month = fields.Char('Requested month', help="Date format = day/month/year(2 digits)", readonly=True)
    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order', readonly=True)
