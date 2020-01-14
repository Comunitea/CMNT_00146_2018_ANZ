# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class ProductAttributeValue(models.Model):

    _inherit = "product.attribute.value"

    def name_get(self):
        """
        Heredo el nombre de la plantilla y si en el contexto viene
        qty_variant_name y una plantilla entonces añado al name_get el
        campo stock de  qty_available o el qty_available_global si la compañia
        tiene padre.
        """
        ctx= self._context.copy()
        a_model = self._context.get('active_model', False)
        if a_model in ('sale.order', 'sale.order.line') and \
                self._context.get('default_product_tmpl_id'):

            tmp_obj = self.env['product.template'].browse(
                self._context.get('default_product_tmpl_id'))

            # Solo si en el producto hay una línea de atributos
            if len(tmp_obj.attribute_line_ids.filtered('main')) == 1:
                p_ids = tmp_obj.product_variant_ids
                res = []
                qty_field = 'qty_available'
                active_model = self._context.get('active_model', False)
                if active_model:
                    id = self._context.get('active_id', False)
                    if id:
                        parent = self.env[active_model].browse(id)

                        if parent and parent.company_id and \
                                parent.company_id.stock_global:
                            qty_field = 'qty_available_global'
                        if parent.warehouse_id:
                            ctx.update(warehouse=parent.warehouse_id.id)
                # Añado el campo stock en al nombre del atributo
                for product in p_ids.with_context(ctx).filtered(
                        lambda x: x.attribute_value_ids):
                    a_value = product.attribute_value_ids.filtered('main')
                    res.append([a_value.id, "%s (%s)" %
                                (a_value.name, product[qty_field])])
                return res
        res = super(ProductAttributeValue, self).name_get()
        return res
