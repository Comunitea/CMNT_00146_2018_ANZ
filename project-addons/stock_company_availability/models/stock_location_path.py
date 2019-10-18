# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

class StockLocationPath(models.Model):
    _inherit = "stock.location.path"

    icc = fields.Boolean('Push intercompany')

    def _apply(self, move):
        if self.icc:
            return super(StockLocationPath, self.sudo())._apply(move=move)
        return super()._apply(move=move)

    def _prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super()._prepare_move_copy_values(move_to_copy=move_to_copy, new_date=new_date)
        push_rule_id = new_move_vals.get('push_rule_id', False)
        if push_rule_id:
            push_rule = self.browse(push_rule_id)
            if push_rule.icc:
                icc_vals = {
                    'sale_line_id': False,
                    'group_id':  False
                    }
                new_move_vals.update(icc_vals)

        if not new_move_vals.get('company_id', False):
            new_move_vals.update(company_id = move_to_copy.company_id.id)
        return new_move_vals