# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class ProductAttributeValue(models.Model):

    _inherit = "product.attribute.value"

    @api.multi
    def name_get(self):
        #Heredo el nombre de la plantilla y si en el contexto viene qty_variant_name y una plantilla entonces ....
        if self._context.get('qty_variant_name', False) and self._context.get('default_product_tmpl_id', False):
            p_ids = self.env['product.product'].search([('product_tmpl_id','=', self._context['default_product_tmpl_id'])])
            res = []
            for a_value in self:
                p_a_value = p_ids.filtered(lambda x: a_value in x.attribute_value_ids)
                res.append([a_value.id, "%s\n(%s)" % (a_value.name, p_a_value.qty_available)])
        else:
            res = super(ProductAttributeValue, self).name_get()
        return res
