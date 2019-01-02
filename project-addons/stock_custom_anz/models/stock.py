# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    to_refund = fields.Boolean(default=True)


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        for line in res.get('product_return_moves', []):
            line[2]['to_refund'] = True
        return res


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def force_set_qty_done(self):
        for picking in self:
            for move in picking.move_lines:
                if not move.quantity_done:
                    move.quantity_done = move.product_uom_qty


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def force_set_qty_done(self):
        for move in self:
            if not move.quantity_done:
                move.quantity_done = move.product_uom_qty


