# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.multi
    def action_view_order_lines(self):

        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference(
            'sale_order_line_tree', 'sale_order_line_tree_view')

        form_view = model_data.get_object_reference(
            'sale_order_line_tree', 'sale_order_line_form_view')

        action = self.env.ref(
            'sale_order_line_tree.sale_order_line_tree_view_action').read()[0]

        action['views'] = {
            (tree_view and tree_view[1] or False, 'tree')}

        action['domain'] = [('id', 'in', self.order_line.ids)]

        action['context'] = {
            'default_order_id': self.id,
            'partner_id': self.partner_id.id,
            'pricelist': self.pricelist_id,
            'company_id': self.company_id.id,
            'type_id': self.type_id.id
        }
        # action['view_ids'] = [tree_view and tree_view[1]]
        action.update(
            {'tax_id': {'domain': [('type_tax_use', '=', 'sale'),
                                   ('company_id', '=', self.company_id)]}})
        return action


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    product_tmpl_id = fields.Many2one('product.template', string="Template")
    variant_sequence = fields.Integer(string="Variant sequence")

    _order = 'sequence, variant_sequence'

    @api.multi
    def write(self, vals):
        return super(SaleOrderLine, self).write(vals)

    @api.multi
    @api.onchange('product_tmpl_id')
    def product_tmpl_id_change(self):
        self.ensure_one()
        self.product_id = False
        result = super(SaleOrderLine, self).product_id_change() or []
        if self.product_tmpl_id:
            result.update({'domain':
                               {'product_id': [('product_tmpl_id', '=', self.product_tmpl_id.id)]}
                           })
        else:
            result.update({'domain':[]})

        return result

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            if not self.product_tmpl_id:
                self.product_tmpl_id = self.product_id.product_tmpl_id

            self.variant_sequence = self.product_id.attribute_value_ids.\
                sequence
        else:
            self.variant_sequence = 0
            self.product_tmpl_id = False
        return result

    @api.model
    def create(self, vals):

        if 'product_tmpl_id'not in vals and vals.get('product_id', False):
            tmpl_id = self.env['product.product'].\
                search_read([('id', '=', vals['product_id'])],
                            ['product_tmpl_id'])[0]['product_tmpl_id'][0]
            vals.update({'product_tmpl_id': tmpl_id})
        return super(SaleOrderLine, self).create(vals)
