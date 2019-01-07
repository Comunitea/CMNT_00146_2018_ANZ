# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields



class StockPicking(models.Model):

    _inherit = 'stock.picking'


    @api.multi
    def get_domain(self):
        my_categ= self.env.ref('stock_picking_custom.res_partner_delivery_carrier')
        if my_categ:
            domain = [('id', 'in', my_categ.partner_ids.ids)]
        else:
            domain = []
        return domain

    delivery_note = fields.Text('Delivery note')
    carrier_partner_id = fields.Many2one('res.partner', string="Carrier partner", domain=lambda self: self.get_domain())
