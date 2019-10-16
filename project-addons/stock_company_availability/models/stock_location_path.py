# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

class StockLocationPath(models.Model):
    _inherit = "stock.location.path"

    def _apply(self, move):
        if self.company_id != move.company_id:
            return super(StockLocationPath, self.sudo())._apply(move=move)
        return super()._apply(move=move)

    def _prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super()._prepare_move_copy_values(move_to_copy=move_to_copy, new_date=new_date)
        if not new_move_vals.get('company_id', False):
            icc_vals = {
                'company_id': move_to_copy.company_id.id,
                'sale_line_id': False,
                'group_id': False,

            }
            new_move_vals.update(icc_vals)

        print ("Valores para el nuevo movimiento\n {}".format(new_move_vals))
        return new_move_vals