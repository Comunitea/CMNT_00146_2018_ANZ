# Copyright 2018 GRAP - Sylvain LE GAL
# Copyright 2018 Tecnativa S.L. - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class PosOrder(models.Model):
    _inherit = 'pos.order'

    return_reason = fields.Text('Return Reason')

    @api.model
    def _process_order(self, pos_order):
        if (not pos_order.get('return') or
                not pos_order.get('returned_order_id')):
            return super()._process_order(pos_order)
        order = super(PosOrder, self)._process_order(pos_order)
        if (pos_order.get('return') or
                pos_order.get('returned_order_id')):
            order.return_reason = pos_order.get('return_reason', '')
        return order
