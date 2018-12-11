# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')

    @api.multi
    def write(self, vals):
        if 'scheduled_sale_id' in vals:
            self.product_variant_ids.write({'scheduled_sale_id': vals['scheduled_sale_id']})

        return super(ProductTemplate, self).write(vals)


    @api.multi
    def unlink_scheduled_templates(self):
        for template in self:
            template.active = any(x.active for x in x.product_variant_ids)
        self.filtered(lambda x: not x.active).unlink()


class ProductProduct(models.Model):

    _inherit = 'product.product'

    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')
    origin_scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')

    @api.multi
    def action_unlink_product(self):
        print (self._context)
        scheduled_sale_id = self._context.get('scheduled_sale_id', False)
        if not scheduled_sale_id:
            return
        return self.env['scheduled.sale'].browse(scheduled_sale_id).open_product_to_cancel(self.ids)


    @api.multi
    def unlink_scheduled_products(self, scheduled_sale_id=[]):
        import ipdb; ipdb.set_trace()
        if not self:
            return
        if scheduled_sale_id:
            scheduled_sale_ids = self.env['scheduled.sale'].browse(scheduled_sale_id)
        else:
            scheduled_sale_ids = self.mapped('scheduled_sale_id')

        for scheduled_sale in scheduled_sale_ids:
            product_ids = self.filtered(lambda x:x.scheduled_sale_id == scheduled_sale)
            template_ids = product_ids.mapped('product_tmpl_ids')
            unlink_vals = {'scheduled_sale_id': False,
                           'origin_scheduled_sale_id': scheduled_sale.id,
                           'active': False}

            ##sale_orders
            ## borro todas las lineas de las lineas de venta, donde estén estos articulos y además escribo un mensaje en los pedidos de venta

            ##ventas de estos productos
            sale_orders = self.env['sale.order.line'].search([('product_id', 'in', product_ids.ids), ('state','!=', 'sale')]).mapped('order_id')


            for sale_order in sale_orders:
                #lineas de venta de estos productos
                lines = sale_order.mapped('order_line').filtered(lambda x:x.product_id in product_ids)

                #genero mensaje para sale_order
                message = _(
                "This sale order has been modified and next lines are unlinked from the schedule sale: <a href=# data-oe-model=schedule.sale data-oe-id=%d>%s</a> <ul>") % (
                      scheduled_sale.id, scheduled_sale.name)
                for line in lines:
                    message = _("{} {}".format(message, "<li>{} Qty: {} </li>".format(line.name, line.product_uom_qty)))
                message = _("{} {}".format(message, "</ul> Date: {}".format(fields.datetime.now())))
                sale_order. message_post(body=message)

                lines.unlink()
            product_ids.write(unlink_vals)
            template_ids.unlink_scheduled_templates()
        return True

    @api.multi
    def archive_scheduled_products(self, scheduled_sale_id=False, undo=True):
        if not scheduled_sale_id:
            return
        template_ids = self.mapped('product_tmpl_id')
        if not undo:
            archive_vals = {'scheduled_sale_id': False, 'origin_scheduled_sale_id': scheduled_sale_id, 'active': True}
        else:
            archive_vals = {'scheduled_sale_id': scheduled_sale_id, 'origin_scheduled_sale_id': False, 'active': True}
        res = self.write(archive_vals)
        template_ids.unlink_scheduled_templates()
        return res
