
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import api, models, fields


class SaleManageVariant(models.TransientModel):
    _inherit = 'sale.manage.variant'

    @api.multi
    def button_transfer_to_order(self):
        sale_order = False
        if 'return_sale_order_line_tree' in self._context:
            context = self.env.context
            record = self.env[context['active_model']].browse(context['active_id'])
            if context['active_model'] == 'sale.order.line':
                sale_order = record.order_id
            else:
                sale_order = record


        res = super(SaleManageVariant, self).button_transfer_to_order()

        if sale_order:

            print ("Lineas: {}".format(sale_order.order_line.ids))
            res_tree = {'domain': [('id', 'in', sale_order.order_line.ids)]}

            return res_tree
        return res