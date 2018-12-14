# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def add_args_to_product_search(self, args=[]):
        args = super(ResPartner, self).add_args_to_product_search(args=args)
        if self._context.get('sale_order_type_id', False):
            sale_type = self.env['sale.order.type'].browse(self._context['sale_order_type_id'])
            brand_ids = sale_type.operating_unit_id.brand_ids.ids
            if brand_ids:
                unit_domain = ['|', ('product_brand_id', '=', False), ('product_brand_id', 'in', brand_ids)]
                args = expression.AND([args, unit_domain])

        return args
