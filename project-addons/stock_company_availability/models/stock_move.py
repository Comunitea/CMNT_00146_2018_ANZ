# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields
from odoo.addons import decimal_precision as dp

STATES_TO_COMPUTE = ['confirmed', 'partially_available']

class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_available_global = fields.Float(related='product_id.qty_available_global')
    global_stock_loc_ids = fields.Many2many('stock.location', string="Other locations (ids)", compute="get_global_stock_loc")
    global_stock_loc_display_name = fields.Char(string="Global info stock", compute="get_global_stock_loc",
                                                help="List of location/available stocks for this product in location of all warehouses and companies. Only info string" )
    @api.multi
    def get_global_stock_loc(self):
        quant_obj = self.env['stock.quant']

        for move in self:
            if move.state in STATES_TO_COMPUTE:
                quants = []

                lot_stock_ids = self.sudo().env['stock.warehouse'].search_read([], ['lot_stock_id'])
                for lot_stock_id in lot_stock_ids:
                    location_id = self.sudo().env['stock.location'].browse(lot_stock_id['lot_stock_id'][0])
                    quant = quant_obj.sudo()._gather(move.product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False)
                    for q in quant:
                        quants.append(q)
                display_name = ''
                ids = []

                for quant in quants:
                    ids += [quant.id]
                    if display_name:
                        display_name = '{} \n/ {}: {}'.format(display_name, quant.location_id.name, quant.quantity - quant.reserved_quantity)
                    else:
                        display_name = '{}: {}'.format(quant.location_id.name,  quant.quantity - quant.reserved_quantity)

                move.global_stock_loc_ids = [(6, 0, ids)]
                move.global_stock_loc_display_name = display_name
            else:
                move.global_stock_loc_ids = [(5)]
                move.global_stock_loc_display_name = None

    def _action_assign(self):
        if self._context.get('force_company', False):
            return super()._action_assign()
        icc_move = self.filtered(lambda x: x.location_id.icc_change)
        moves = self.filtered(lambda x: not x.location_id.icc_change)
        ctx = self._context.copy()

        if icc_move:
            company_ids = icc_move.mapped('company_id')
            for company_id in company_ids:
                ctx.update(force_company=company_id.id)
                move_company = icc_move.with_context(ctx).filtered(lambda x: x.company_id == company_id)
                super(StockMove, move_company).sudo()._action_assign()
        if moves:
            company_ids = moves.mapped('company_id')
            for company_id in company_ids:
                ctx.update(force_company=company_id.id)
                move_company = moves.with_context(ctx).filtered(lambda x: x.company_id == company_id)
                super(StockMove, move_company)._action_assign()

    def _action_cancel(self):
        ##Heredo para cancelar los albaranes intercompañias.
        moves_to_cancel = self.sudo().filtered(lambda m: m.state != 'cancel' and any(m.move_dest_ids.mapped('push_rule_id.icc')))
        for move in moves_to_cancel:
            dest_ic_moves = move.sudo().move_dest_ids.filtered(lambda x: x.company_id != move.company_id)
            if dest_ic_moves:
                siblings_states = (dest_ic_moves.mapped('move_orig_ids') - move).mapped('state')
                if all(state == 'cancel' for state in siblings_states):
                        dest_ic_moves.filtered(lambda m: m.state != 'done')._action_cancel()
                else:
                    if all(state in ('done', 'cancel') for state in siblings_states):
                        dest_ic_moves.write({'procure_method': 'make_to_stock'})
                        dest_ic_moves.write({'move_orig_ids': [(3, move.id, 0)]})
        return super()._action_cancel()

    def get_auto_done(self, moves_todo):

        ##Busco los siguientes con sudo()
        auto_done_ids = moves_todo.sudo().mapped('move_dest_ids').filtered(
            lambda x: x.picking_type_id.auto_done and x.state == 'assigned')
        ctx = self._context.copy()

        for move_dest in auto_done_ids.filtered(lambda x: all(x.state=='done' for x in x.move_orig_ids)):
            ctx.update(force_company=move_dest.company_id.id)
            move = move_dest.with_context(ctx)
            for line in move.move_line_ids:
                line.qty_done = line.product_uom_qty
            move._action_done()

    @api.multi
    def _action_done(self):

        ctx = self._context.copy()
        moves_todo = super()._action_done()
        self.get_auto_done(moves_todo)

        for move in moves_todo:
            move_dest_ids_ic = move.sudo().mapped('move_dest_ids').filtered(lambda x: x.company_id != move.company_id)
            if move_dest_ids_ic:
                for move in move_dest_ids_ic:
                    move.sudo()._action_assign()
                    ctx.update(force_company=move.sudo().company_id.id)
                    move_ic = move.with_context(ctx)


                    if move_ic.picking_type_id.auto_done:
                        move_ic._action_done()


        return moves_todo

