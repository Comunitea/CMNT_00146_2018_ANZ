# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields
from odoo.addons import decimal_precision as dp

STATES_TO_COMPUTE = ['assigned', 'partially_available']

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_picking_move_tree(self):
        ctx = self._context.copy()
        if any(x.state in ('confirmed', 'partially_available') for x in self.move_lines):
            state = 'partially_available'
        ctx.update(picking_code=self.picking_type_id.code, picking_state=state)
        print (ctx)
        return super(StockPicking, self.with_context(ctx)).action_picking_move_tree()







