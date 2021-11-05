# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        ctx = self.env.context.copy()
        from_website = ctx.get('from_website', False)

        if from_website:
            team_id = vals.get('team_id', False)
            domain = []
            if team_id:
                domain = [('id', '=', team_id)]
            type_id = self.recalculate_type_id(domain)
            if type_id:
                vals.update({
                    'type_id': type_id.id
                })

        return super(SaleOrder, self).create(vals)

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.team_id:
            domain = [('id', '=', self.team_id.id)]
            type_id = self.recalculate_type_id(domain)
            if type_id:
                self.type_id = type_id.id

    def recalculate_type_id(self, domain):
        order_type = request.env['crm.team'].sudo().search(domain, limit=1).team_type
        if order_type == 'website':
            website = request.env['website'].get_current_website()
            return website.sale_type_id

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """
           Workaround to pass warehouse in product context while stock locations will NOT are defined by company.
           It avoid consider stock for locations out of current website range.
           It was needed to override website_sale_stock module method for pass warehouse in context.
       """
        values = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        line_id = values.get('line_id')

        for line in self.order_line:
            if line.product_id.type == 'product' and line.product_id.inventory_availability in ['always', 'threshold']:
                cart_qty = sum(self.order_line.filtered(
                    lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty'))
                if cart_qty > line.product_id.with_context(
                        warehouse=self.website_id.warehouse.id).qty_available and (line_id == line.id):
                    qty = line.product_id.with_context(
                        warehouse=self.website_id.warehouse.id).qty_available - cart_qty
                    new_val = super(SaleOrder, self)._cart_update(line.product_id.id, line.id, qty, 0, **kwargs)
                    values.update(new_val)

                    # Make sure line still exists, may have been deleted in super()_cartupdate because qty can be <= 0
                    if line.exists() and new_val['quantity']:
                        line.warning_stock = _('You ask for %s products but only %s is available') % (
                            cart_qty, new_val['quantity'])
                        values['warning'] = line.warning_stock
                    else:
                        self.warning_stock = _("Some products became unavailable and your cart has been updated. "
                                               "We're sorry for the inconvenience.")
                        values['warning'] = self.warning_stock
        return values
