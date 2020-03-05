# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.depends('order_line')
    def _compute_sale_order_line_count(self):
        for order in self:
            order.sale_order_line_count = len(order.order_line)
            order.sale_order_line_template_count = len(order.template_lines)

    sale_order_line_template_count = fields.Integer(
        'Template line count', compute='_compute_sale_order_line_count')
    template_lines = fields.One2many('sale.order.line.template.group',
                                     'order_id')

    @api.multi
    def action_view_order_lines_template_group(self):

        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference(
            'sale_order_line_tree', 'view_sale_order_line_group_template_tree')

        action = self.env.ref(
            'sale_order_line_tree.view_sale_order_line_group_template_tree_action').read()[0]
        action['views'] = {
            (tree_view and tree_view[1] or False, 'tree')}

        action['domain'] = [('order_id', '=', self.id)]

        action['context'] = {}
        return action

    @api.multi
    def action_view_order_lines(self):

        self.ensure_one()
        if not self.partner_id or not self.pricelist_id or not self.company_id.id or not self.type_id:
            raise ValidationError('Revisa los campos cliente, tarifa, compañia y tipo de venta')

        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference(
            'sale_order_line_tree', 'sale_order_line_tree_view')

        action = self.env.ref(
            'sale_order_line_tree.sale_order_line_tree_view_action').read()[0]

        action['views'] = {
            (tree_view and tree_view[1] or False, 'tree')}

        action['domain'] = [('order_id', '=', self.id)]

        action['context'] = {
            'default_order_id': self.id,
            'partner_id': self.partner_id.id,
            'pricelist': self.pricelist_id,
            'company_id': self.company_id.id,
            'type_id': self.type_id.id,
        }
        # action['view_ids'] = [tree_view and tree_view[1]]
        action.update(
            {'tax_id': {'domain': [('type_tax_use', '=', 'sale'),
                                   ('company_id', '=', self.company_id)]}}
             )


        return action


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    product_tmpl_id = fields.Many2one("product.template", string="Template")
    variant_sequence = fields.Integer(string="Variant sequence")

    _order = 'sequence, variant_sequence'

    @api.multi
    def write(self, vals):
        if 'product_tmpl_id' not in vals and vals.get('product_id', False):
            tmpl_id = self.env['product.product'].\
                search_read([('id', '=', vals['product_id'])],
                            ['product_tmpl_id'])
            vals.update({
                'product_tmpl_id':
                tmpl_id and tmpl_id[0]['product_tmpl_id'][0]})
        return super(SaleOrderLine, self).write(vals)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.product_tmpl_id = self.product_id.product_tmpl_id
            self.variant_sequence = self.product_id.attribute_value_ids.\
                filtered('main').sequence
        else:
            self.variant_sequence = 0
        return result

    @api.model
    def create(self, vals):
        if 'product_tmpl_id' not in vals and vals.get('product_id', False):
            tmpl_id = self.env['product.product'].\
                search_read([('id', '=', vals['product_id'])],
                            ['product_tmpl_id'])
            vals.update({
                'product_tmpl_id':
                tmpl_id and tmpl_id[0]['product_tmpl_id'][0]})
        return super(SaleOrderLine, self).create(vals)
