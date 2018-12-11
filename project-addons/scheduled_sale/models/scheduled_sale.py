# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ScheduleSalePeriod(models.Model):
    _name = 'scheduled.sale.period'

    active = fields.Boolean('Active', default=True)
    name = fields.Char('Name', required=True)
    from_date = fields.Date('From date', required=True)
    to_date = fields.Date('To date', required=True)
    scheduled_sale_ids = fields.One2many('scheduled.sale', 'period_id', string="Orders")


class ScheduleSale(models.Model):

    _name = 'scheduled.sale'
    _description = 'Schedule sale'

    @api.multi
    @api.depends('scheduled_orders_ids')
    def _compute_sale_orders_count(self):
        for order in self:
            order.scheduled_orders_ids_count = len(order.scheduled_orders_ids)

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

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('end', 'Ended')
        ], 'Status', default='draft', index=True, required=True, track_visibility='always')

    scheduled_orders_ids = fields.One2many('sale.order', 'scheduled_sale_id', string="Orders")
    scheduled_orders_ids_count = fields.Integer('Sale orders count', compute='_compute_sale_orders_count')

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

        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference(
            'sale', 'view_order_tree')

        form_view = model_data.get_object_reference(
            'sale', 'view_order_form')

        action = self.env.ref(
            'scheduled_sale.action_scheduled_sale_orders_tree').read()[0]
        action['views'] = {
            (tree_view and tree_view[1] or False, 'tree'),
            (form_view and form_view[1] or False, 'form')}

        action['domain'] = [('scheduled_sale_id','=',self.id)]

        action['context'] = {'default_scheduled_sale_id': self.id,
                             'default_origin': self.code,
                             'default_validity_date': self.period_id.to_date
                             }
        return action
