# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def _default_ref_change_code(self):
        return self.env['ir.sequence'].next_by_code('product.template.ref_change_code')

    @api.multi
    def _compute_attribute_line_ids_count(self):
        for tmpl in self:
            tmpl.attribute_line_ids_count = len(tmpl.attribute_line_ids.filtered(lambda x:x.value_ids))

    ref_change_code = fields.Char(default=_default_ref_change_code)
    attribute_line_ids_count = fields.Integer(compute="_compute_attribute_line_ids_count")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        sale_order = self.env['sale.order'].get_sale_order_by_context()
        if sale_order:
            args = sale_order.add_args_to_product_search(args)
        return super(ProductTemplate, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)



class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        sale_order = self.env['sale.order'].get_sale_order_by_context()
        if sale_order:
            args = sale_order.add_args_to_product_search(args)
        return super(ProductProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
