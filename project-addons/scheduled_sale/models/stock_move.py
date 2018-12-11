# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields

class StockMove(models.Model):
    _inherit = "stock.move"

    deliver_month = fields.Char('Requested month', help="Date format = day/month/year(2 digits)", readonly=True)
    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order', readonly=True)

    def _prepare_procurement_values(self):
        values = super(StockMove, self)._prepare_procurement_values()
        if self.deliver_month:
            values.update({
                'deliver_month': self.deliver_month,
                'scheduled_sale_id': self.scheduled_sale_id.id})
        return values

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        vals.update({
            'deliver_month': self.deliver_month,
            'scheduled_sale_id': self.scheduled_sale_id.id})
        return vals


    def _assign_picking(self):
        not_scheduled_moves = self.filtered(lambda x: x.deliver_month=='')
        if not_scheduled_moves:
            super(StockMove, not_scheduled_moves)._assign_picking()
        scheduled_moves = self - not_scheduled_moves
        if not scheduled_moves:
            return True

        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """

        Picking = self.env['stock.picking']
        for move in scheduled_moves:
            recompute = False
            picking = Picking.search([
                ('deliver_month', '=', move.deliver_month),
                ('scheduled_sale_id', '=', move.scheduled_sale_id.id),
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
            if picking:
                if picking.partner_id.id != move.partner_id.id or picking.origin != move.origin:
                    # If a picking is found, we'll append `move` to its move list and thus its
                    # `partner_id` and `ref` field will refer to multiple records. In this
                    # case, we chose to  wipe them.
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            move._assign_picking_post_process(new=recompute)
            # If this method is called in batch by a write on a one2many and
            # at some point had to create a picking, some next iterations could
            # try to find back the created picking. As we look for it by searching
            # on some computed fields, we have to force a recompute, else the
            # record won't be found.
            if recompute:
                move.recompute()
        return True
