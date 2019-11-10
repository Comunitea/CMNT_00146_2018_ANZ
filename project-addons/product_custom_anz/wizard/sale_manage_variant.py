# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.addons.decimal_precision as dp
from odoo import api, models, fields


class SaleManageVariant(models.TransientModel):

    _inherit = 'sale.manage.variant'

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """
        OVERWRITED
        """
        self.variant_line_ids = [(6, 0, [])]
        template = self.product_tmpl_id
        context = self.env.context
        record = self.env[context['active_model']].browse(
            context['active_id'])
        if context['active_model'] == 'sale.order.line':
            sale_order = record.order_id
        else:
            sale_order = record
        # OVERWRITED, MOSTRAR SOLO LOS QUE CREAN VARIANTE PERO NO ESTAN COMO
        # FEATURES
        attr_lines = template.attribute_line_ids.filtered(
            lambda x: x.attribute_id.create_variant and not
            x.attribute_id.feature
        )
        num_attrs = len(attr_lines)
        if not template or not num_attrs or num_attrs > 2:
            return
        line_x = attr_lines[0]
        line_y = False if num_attrs == 1 else attr_lines[1]
        lines = []
        for value_x in line_x.value_ids:
            for value_y in line_y and line_y.value_ids or [False]:
                product = self._get_product_variant(value_x, value_y)
                if not product:
                    continue
                order_line = sale_order.order_line.filtered(
                    lambda x: x.product_id == product
                )[:1]
                lines.append((0, 0, {
                    'value_x': value_x,
                    'value_y': value_y,
                    'product_uom_qty': order_line.product_uom_qty,
                }))
        self.variant_line_ids = lines