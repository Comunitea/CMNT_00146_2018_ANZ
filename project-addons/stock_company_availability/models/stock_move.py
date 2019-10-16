# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields
from odoo.addons import decimal_precision as dp

STATES_TO_COMPUTE = ['assigned', 'partially_available']

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
            if move.state not in STATES_TO_COMPUTE:
                quants = []
                if move.state in ['confirmed', 'partially_available']:
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

        company_ids = self.mapped('company_id')
        ctx = self._context.copy()
        for company_id in company_ids:
            ctx.update(force_company=company_id.id)
            move_company = self.with_context(ctx).filtered(lambda x: x.company_id == company_id)
            super(StockMove, move_company)._action_assign()









