# -*- coding: utf-8 -*-
# © 2016 Comunitea - Kiko Sanchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.addons.stock.models.product import OPERATORS



class StockMove(models.Model):


    def _get_ic_move_values(self,location_id, location_dest_id):
        self.ensure_one()
        return {
            'name': _('IC:') + (self.name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.qty_done,
            'date': self.date,
            #'company_id': self.inventory_id.company_id.id,
            #'inventory_id': self.inventory_id.id,
            'state': 'confirmed',
            #'restrict_partner_id': self.partner_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.prod_lot_id.id,
                'product_uom_qty': 0,  # bypass reservation here
                'product_uom_id': self.product_uom_id.id,
                'qty_done': self.qty_done,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            })]
        }

    def _action_done(self):
        res = super()._action_done()
        if self.picking_id and self.picking_id.picking_type_id.id ==8:
            self.create_intercompany_stock_moves()

    def create_intercompany_stock_moves(self):

        #Se realizan moveimientos de stock para compensar


        self = self.sudo()
        anzamar = self.env['res.company'].browse(1)
        bemar = self.env['res.company'].browse(3)
        anzamar_stock_loc = 12
        bemar_stock_loc = 20

        # salida desde anzamar
        ctx = self._context.copy()
        ctx.update(force_company=1)
        move = self.with_context(ctx)
        vals = move._get_ic_move_values(anzamar_stock_loc, anzamar.partner_id.property_stock_customer.id)
        move.create(vals)
        move.action_done()

        # salida hacia bemar
        ctx = self._context.copy()
        ctx.update(force_company=3)
        move = self.with_context(ctx)
        vals = move._get_ic_move_values(anzamar.partner_id.property_stock_supplier.id, bemar_stock_loc)
        move.create(vals)
        move.action_done()

        move_in
