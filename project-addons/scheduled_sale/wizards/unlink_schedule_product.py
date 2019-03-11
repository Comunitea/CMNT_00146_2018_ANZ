# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models


class UnlinkScheduleProductLine(models.TransientModel):
    _name = 'unlink.schedule.product.line'
    _order = 'product_tmpl_id, product_active desc, product_id'

    @api.multi
    @api.depends('product_id')
    def get_qty_ordered(self):
        sale_line_obj = self.env["sale.order.line"]
        for line in self:
            sale_lines = sale_line_obj.\
                search([('scheduled_sale_id', '=',
                         line.unlink_schedule_product_id.scheduled_sale_id.id),
                        ('product_id', '=', line.product_id.id)])
            line.product_qty_scheduled = \
                sum(sale_lines.mapped('product_uom_qty'))

    product_id = fields.Many2one('product.product')
    product_active = fields.Boolean(related="product_id.active", store=True)
    product_tmpl_id = fields.Many2one('product.template')
    to_cancel = fields.Boolean('To cancel', default=False)
    unlink_schedule_product_id = fields.Many2one('unlink.schedule.product.wzd')
    product_qty_scheduled = fields.Float("Qty ordered", compute="get_qty_ordered", store=True)
    scheduled_sale_id = fields.Many2one(related='unlink_schedule_product_id.scheduled_sale_id')
    @api.multi
    def set_product_as_cancel(self, to_cancel=False):
        self.browse(self._context.get('active_ids', [])).write({'to_cancel': to_cancel})

    @api.multi
    def action_unlink_product(self):

        if self._context.get('from_tree', False):
            line_to_active = self.filtered(lambda x: x.product_id.active)
            line_to_active.mapped('product_id').action_unlink_product()
        return


    @api.multi
    def set_product_as_cancel(self, to_cancel=False):
        self.browse(self._context.get('active_ids', [])).write({'to_cancel': to_cancel})
        return self.open_wzd()

    @api.multi
    def open_wzd(self):

        view = self.env.ref('scheduled_sale.unlink_schedule_product_form')
        line = self.env['unlink.schedule.product.line'].browse(self._context.get('active_id', False))
        new = line and line.unlink_schedule_product_id
        action = {
            'name': _('Unlink products Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'unlink.schedule.product.wzd',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': new.id,
            'context': dict(self.env.context)}
        return action


class UnlinkScheduleProductWzd(models.TransientModel):
    _name = 'unlink.schedule.product.wzd'

    scheduled_sale_id = fields.Many2one('scheduled.sale', readonly=True)
    line_ids = fields.One2many('unlink.schedule.product.line', 'unlink_schedule_product_id')
    origin_product_ids = fields.One2many('unlink.schedule.product.line', 'unlink_schedule_product_id', domain=[('to_cancel','=',False)])
    to_cancel_product_ids = fields.One2many('unlink.schedule.product.line', 'unlink_schedule_product_id', domain=[('to_cancel', '=', True)])
    name = fields.Char(related="scheduled_sale_id.name")
    code = fields.Char(related="scheduled_sale_id.code")
    period_id = fields.Many2one(related="scheduled_sale_id.period_id")
    product_brand_id = fields.Many2one(related="scheduled_sale_id.product_brand_id")

    @api.model
    def default_get(self, fields):
        res = super(UnlinkScheduleProductWzd, self).default_get(fields)
        return res

    @api.multi
    def unlink_product(self):
        self.ensure_one()

        to_cancel_product = self.to_cancel_product_ids.mapped('product_id')
        to_cancel_product.unlink_scheduled_products(self.scheduled_sale_id.id)
        self.origin_product_ids.filtered(lambda x: not x.product_active).write({'product_active': True})

        return {
            'name': 'Schedule sales',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form, tree',
            'res_model': 'scheduled.sale',
            'target': 'self',
            'res_id': self.scheduled_sale_id.id,
            'context': dict(self.env.context)}
