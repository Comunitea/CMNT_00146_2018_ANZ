# -*- coding: utf-8 -*-
# © 2018 Comunitea - Omar Castiñeira Saavedra <omar@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models

class SaleManageVariant(models.TransientModel):

    _inherit = 'sale.manage.variant'

    @api.model
    def _get_default_partner(self):
        if self._context.get('active_id', False) and \
                self._context.get('active_model', False):
            if self._context['active_model'] == 'sale.order':
                active_id = self._context['active_id']
            elif self._context['active_model'] == 'sale.order.line':
                line_id = self._context['active_id']
                active_id = self.env['sale.order.line'].browse(line_id).\
                    order_id.id

            if active_id:
                order = self.env['sale.order'].browse(active_id)
                return order.partner_id.commercial_partner_id.id
            return False

    partner_id = fields.Many2one("res.partner", "Customer",
                                 default=_get_default_partner)

    default_variant_id = fields.Many2one(comodel_name='product.attribute')

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
       if self.product_tmpl_id and len(self.product_tmpl_id.attribute_line_ids)==1:

           self.default_variant_id = self.product_tmpl_id.attribute_line_ids.attribute_id
           print (self.default_variant_id)
       super(SaleManageVariant, self)._onchange_product_tmpl_id()

    @api.model
    def default_get(self, fields):
        res = super(SaleManageVariant, self).default_get(fields)
        return res

    # Sobrescribo para añadir el onchange del discount y que funcio
    # con tarifas que muestran el precio fuera del descuento
    @api.multi
    def button_transfer_to_order(self):
        context = self.env.context
        record = self.env[context['active_model']].browse(context['active_id'])
        if context['active_model'] == 'sale.order.line':
            sale_order = record.order_id
        else:
            sale_order = record
        OrderLine = self.env['sale.order.line']
        lines2unlink = OrderLine
        for line in self.variant_line_ids:
            product = self._get_product_variant(line.value_x, line.value_y)
            order_line = sale_order.order_line.filtered(
                lambda x: x.product_id == product
            )
            if order_line:
                if not line.product_uom_qty:
                    # Done this way because there's a side effect removing here
                    lines2unlink |= order_line
                else:
                    order_line.product_uom_qty = line.product_uom_qty
            elif line.product_uom_qty:
                vals = OrderLine.default_get(OrderLine._fields.keys())
                vals.update({
                    'product_id': product.id,
                    'product_uom': product.uom_id,
                    'product_uom_qty': line.product_uom_qty,
                    'order_id': sale_order.id,
                })
                order_line = OrderLine.new(vals)
                order_line.product_id_change()
                order_line._onchange_discount()
                order_line_vals = order_line._convert_to_write(
                    order_line._cache)
                sale_order.order_line.browse().create(order_line_vals)
        lines2unlink.unlink()
