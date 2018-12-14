# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    scheduled_sale_id = fields.\
        Many2one('scheduled.sale', 'Schedule order', readonly=True)
    origin_scheduled_sale_id = fields.\
        Many2one('scheduled.sale', 'Schedule order', readonly=True)

    @api.onchange('scheduled_sale_id')
    def scheduled_sale_id_change(self):
        if self.scheduled_sale_id:
            self.pricelist_id = self.scheduled_sale_id.pricelist_id
        else:
            self.onchange_partner_id()

    @api.multi
    def action_view_order_lines_template_group(self):
        action = super(SaleOrder, self).action_view_order_lines_template_group()
        if self.scheduled_sale_id:
            action['context'].update({'show_deliver_month': False})
        return action

    @api.multi
    def action_draft(self):
        if self.mapped('scheduled_sale_id').filtered(lambda x: x.state in ('cancel', 'done')):
            raise ValidationError(_("You can't re-order sale order with out scheduled sale in confirm state"))
        return super(SaleOrder, self).action_draft()

    @api.multi
    def _action_confirm(self):
        if self.mapped('scheduled_sale_id').filtered(lambda x:x.state=='draft'):
            raise ValidationError(_("You can't confirm sale order with scheduled sale in draft state"))
        return super(SaleOrder, self)._action_confirm()


    def add_args_to_product_search(self, args):
        args = super(SaleOrder, self).add_args_to_product_search(args)
        if self.scheduled_sale_id:
            args = expression.AND([args, [('scheduled_sale_id', '=', self.scheduled_sale_id.id)]])
        elif self._context('scheduled_sale_id', False):
            args = expression.AND([args, [('scheduled_sale_id', '=', self._context['scheduled_sale_id'])]])
        return args

    @api.multi
    def action_view_order_lines(self):
        action = super(SaleOrder, self).action_view_order_lines()
        if self.scheduled_sale_id:

            action['context'].update(default_scheduled_sale_id=self.scheduled_sale_id.id)
        return action
        #action.update(
        #    {'tax_id': {'domain': [('type_tax_use', '=', 'sale'),
        #                           ('company_id', '=', self.company_id)]}}
        #)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    scheduled_sale_id = fields.Many2one('scheduled.sale', 'Schedule order')
    deliver_month = fields.Char('Requested month', help="Date format = day/month/year(2 digits)")

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.scheduled_sale_id = self.product_id.scheduled_sale_id
        return result


    @api.multi
    @api.onchange('requested_date')
    def onchange_requested_date(self):
        for line in self.filtered(lambda x: x.requested_date):

            line.deliver_month = datetime.strptime(line.requested_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime('%B/%y')

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be created from a procurement rule
        comming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        values.update({
            'scheduled_sale_id': self.order_id.scheduled_sale_id.id,
            'deliver_month': self.deliver_month})
        return values

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.order_id.scheduled_sale_id:
            return super(SaleOrderLine,self)._onchange_product_id_check_availability()
        return {}

