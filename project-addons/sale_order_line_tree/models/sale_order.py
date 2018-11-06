# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models, fields
from odoo.osv import expression

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.depends('order_line')
    def _compute_sale_order_line_count(self):
        for order in self:
            order.sale_order_line_count = len(order.order_line)

    sale_order_line_count = fields.Integer('Order line count', compute='_compute_sale_order_line_count')


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
            (tree_view and tree_view[1] or False, 'tree'),
            (form_view and form_view[1] or False, 'form')}

        action['domain'] = [('id', 'in', self.order_line.ids)]

        action['context'] = {
            'default_order_id': self.id,
            'partner_id': self.partner_id.id,
            'pricelist': self.pricelist_id,
            'company_id': self.company_id.id,
            'type_id': self.type_id.id
        }
        #action['view_ids'] = [tree_view and tree_view[1]]
        action.update({'tax_id':
                        {'domain': [('type_tax_use', '=', 'sale'), ('company_id', '=', self.company_id)]}
                       })

        return action

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_tmpl_id = fields.Many2one('product.template', string="Template")


    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.product_tmpl_id = self.product_id.product_tmpl_id
        else:
            self.product_tmpl_id = False
        return result

    @api.model
    def create(self, vals):

        if not 'product_tmpl_id' in vals and vals.get('product_id', False):
            tmpl_id = self.env['product.product'].search_read([('id','=', vals['product_id'])], ['product_tmpl_id'])[0]['product_tmpl_id'][0]
            vals.update({'product_tmpl_id': tmpl_id})
        return super(SaleOrderLine, self).create(vals)
