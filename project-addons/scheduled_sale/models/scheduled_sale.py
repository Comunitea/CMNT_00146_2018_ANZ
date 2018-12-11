# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models

class ScheduleSalePeriod(models.Model):
    _name = 'scheduled.sale.period'

    active = fields.Boolean('Active', default=True)
    name = fields.Char('Name')
    from_date = fields.Date('From date')#, readonly=False)# , states={'end':[('readonly',True)],'confirm':[('readonly',True)]})
    to_date = fields.Date('To date')# , readonly=False)#, states={'end':[('readonly',True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('end', 'Ended')],
        'Status', default='draft', index=True, required=True, track_visibility='always')
    scheduled_sale_ids = fields.One2many('scheduled.sale', 'period_id', string="Orders")

class ScheduleSale(models.Model):

    _name = 'scheduled.sale'
    _description = 'Schedule sale'

    @api.multi
    @api.depends('scheduled_orders_ids')
    def _compute_sale_orders_count(self):
        for order in self:
            order.scheduled_orders_ids_count = len(order.scheduled_orders_ids)

    @api.multi
    @api.depends('product_ids')
    def _compute_product_count(self):
        for order in self:
            order.product_ids_count = len(order.product_ids)

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    active = fields.Boolean('Active', default=True)
    period_id = fields.Many2one('scheduled.sale.period', string="Period")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('scheduled.sale'))
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=False,
                                   help="Pricelist for scheduled sale.",
                                   states = {'confirm': [('readonly', True)], 'end': [('readonly', True)]})

    product_brand_id = fields.Many2one('product.brand', string='Brand')
    product_ids = fields.One2many('product.product', 'scheduled_sale_id',
                     string="Products in this schedule")
    product_ids_count = fields.Integer('Product count', compute='_compute_product_count')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('done', 'Ended')
        ], 'Status', default='draft', index=True, required=True, track_visibility='always')

    scheduled_orders_ids = fields.One2many('sale.order', 'scheduled_sale_id', string="Orders")
    scheduled_orders_ids_count = fields.Integer('Sale orders count', compute='_compute_sale_orders_count')

    @api.multi
    def _cancel_schedule(self):
        for self_id in self:
            self_id.state = 'cancel'
            self_id.scheduled_orders_ids.action_cancel()
        return True

    @api.multi
    def cancel_schedule(self):

        yes_confirmation = self._context.get('yes_confirmation', False)
        if not yes_confirmation:
            vals = {'function': 'cancel_schedule()',
                    'name': 'Cancel schedule order',
                    'question': _('Are you sure?. You will cancel all sale orders asociated to this schedules sale')}
            return self.env['yesno.confirmation'].with_context(self._context).return_wzd(self, vals)
        else:
            return_id = self._context.get('return_id')
            ctx = self._context.get('ctx', self._context)
            ctx.update(yes_confirmation=False)
            if return_id:
                self_id = self.browse(return_id).with_context(ctx)
                return self_id._cancel_schedule()
            return False


    @api.multi
    def _done_schedule(self):
        for self_id in self:
            self_id.state = 'done'
            #COnfirmo los pedidos ????
            self_id.scheduled_orders_ids.filtered(lambda x:x.state in ('draft', 'sent')).action_confirm()
            self.product_ids.archive_scheduled_products(self.id)

        self.env['product.product'].archive_from_scheduled_sale(self.ids)
        return True

    @api.multi
    def done_schedule(self):

        yes_confirmation = self._context.get('yes_confirmation', False)
        if not yes_confirmation:
            vals = {'function': 'done_schedule()',
                    'name': 'Set as done',
                    'question': _('Are you sure?. You will change this products, and change the pricelist')}
            return self.env['yesno.confirmation'].with_context(self._context).return_wzd(self, vals)
        else:
            return_id = self._context.get('return_id')
            ctx = self._context.get('ctx', self._context)
            ctx.update(yes_confirmation=False)
            if return_id:
                self_id = self.browse(return_id).with_context(ctx)
                return self_id._done_schedule()

            return False

    @api.multi
    def write(self, vals):
        if 'state' in vals and vals.get('state', '') == 'cancel':
            self.mapped('scheduled_orders_ids').action_cancel()

        return super(ScheduleSale, self).write(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        names1 = super(models.Model, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        # Make the other search
        names2 = []
        if name:
            domain = [('code', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        # Merge both results
        return list(set(names1) | set(names2))[:limit]


    @api.multi
    def action_show_schedule_orders(self):
        action = self.env.ref(
            'scheduled_sale.action_scheduled_sale_orders_tree').read()[0]
        sale_ids = self.mapped('scheduled_orders_ids')
        if not sale_ids or len(sale_ids) > 1:
            action['domain'] = "[('id','in',%s)]" % (sale_ids.ids)
        elif len(sale_ids) == 1:
            res = self.env.ref('sale.view_order_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = sale_ids.id

        action['context'] = {'default_scheduled_sale_id': self.id,
                             'default_origin': self.code,
                             'default_validity_date': self.period_id.to_date}
        return action

    @api.multi
    def open_all_product_to_cancel(self):
        return self.open_product_to_cancel(all_products=True)

    @api.multi
    def open_product_to_cancel(self, cancel_ids=[], all_products=False):

        wzd_vals = dict(scheduled_sale_id=self.id,
                    origin_product_ids=[(0, 0, dict(
                                            product_id=product.id,
                                            product_tmpl_id=product.product_tmpl_id.id
                                        )) for product in self.product_ids])
        new = self.env['unlink.schedule.product.wzd'].create(wzd_vals)
        if all_products:
            view = self.env.ref('scheduled_sale.unlink_scheduled_product_tree')
            return {
                'name': 'Unlink products Operations',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'unlink.schedule.product.line',
                'views': [(view.id, 'tree')],
                'view_id': view.id,
                'target': 'self',
                'domain': [('id', 'in', new.origin_product_ids.ids)],
                'context': dict(self.env.context)}

        else:
            view = self.env.ref('scheduled_sale.unlink_schedule_product_form')
            if cancel_ids:
                new.origin_product_ids.filtered(lambda x:x.product_id.id in cancel_ids).write({'to_cancel':True})
            return {
                'name': 'Unlink products Operations',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'unlink.schedule.product.wzd',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': new.id,
                'context': dict(self.env.context)}

