# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    scheduled_sale_id = fields.Many2one('scheduled.sale', string='Active schedule order')
    origin_scheduled_sale_id = fields.Many2one('scheduled.sale', string='Archived Schedule order')

    @api.multi
    def write(self, vals):
        return super(ProductTemplate, self).write(vals)


    @api.multi
    def archive_scheduled_template(self, scheduled_sale_id = False, undo=True):
        if not scheduled_sale_id:
            return

        for template in self:
            if not undo:
                archive_vals = {'scheduled_sale_id': False, 'origin_scheduled_sale_id': scheduled_sale_id}
            else:
                archive_vals = {'scheduled_sale_id': scheduled_sale_id, 'origin_scheduled_sale_id': False}
            template.write(archive_vals)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        schedule_sale_id = self.env['scheduled.sale'].get_scheduled_sale_by_context()
        if schedule_sale_id:
            args = schedule_sale_id.add_args_to_product_search(args)

        return super(ProductTemplate, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                   access_rights_uid=access_rights_uid)


class ProductProduct(models.Model):

    _inherit = 'product.product'

    #scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')

    @api.multi
    def action_unlink_product(self):

        scheduled_sale_id = self._context.get('scheduled_sale_id', False)
        if not scheduled_sale_id:
            return
        return self.env['scheduled.sale'].browse(scheduled_sale_id).open_product_to_cancel(self.ids, re_order=self._context.get('re_order', False))


    @api.multi
    def unlink_scheduled_products(self, scheduled_sale_id=[]):

        ##Unlink products if in sale orders
        ## Implica desactivar los productos, sacarlos de las ordenes de venta y post en el saleorder

        if not self or not scheduled_sale_id:
            raise ValidationError (_('No products to unlink, or not schedule sale'))
        ##ventas de estos productos.
        sale_orders = self.env['sale.order.line'].search([('product_id', 'in', self.ids), ('order_id.scheduled_sale_id','=', scheduled_sale_id), ('state','in', ['draft', 'sent'])]).mapped('order_id')

        for sale_order in sale_orders:
            #lineas de venta de estos productos
            lines = sale_order.mapped('order_line').filtered(lambda x:x.product_id in self)

            #genero mensaje para sale_order
            message = _(
                "This sale order has been modified and next lines are unlinked from the schedule sale: <a href=# data-oe-model=scheduled.sale data-oe-id=%d>%s</a> <ul>") % (
                scheduled_sale_id, sale_order.scheduled_sale_id.name)
            for line in lines:
                message = _("{} {}".format(message, "<li>{} Qty: {} </li>".format(line.name, line.product_uom_qty)))

            message = _("{} {}".format(message, "</ul> Date: {}".format(fields.datetime.now())))
            sale_order.message_post(body=message)

            lines.unlink()
        for product in self:
            if len(product.product_tmpl_id.filtered('active')) == 1:
                product.product_tmpl_id.active = False
            else:
                product.write({'active': False})
        return True

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        schedule_sale_id = self.env['scheduled.sale'].get_scheduled_sale_by_context()
        if schedule_sale_id:
            args = schedule_sale_id.add_args_to_product_search(args)
        return super(ProductProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                   access_rights_uid=access_rights_uid)
