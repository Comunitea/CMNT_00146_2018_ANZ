# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api, _
from odoo.http import request


class ProductProduct(models.Model):
    """ Eliminar cuando todos los artículos se creen con el importador
        TODO: Add supplier name
    """
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Original search
        names1 = super().name_search(
            name=name, args=args, operator=operator, limit=limit)
        # Make the other search
        names2 = []
        if name:
            domain = [('product_tmpl_id.ref_template_name', operator, name)]
            if not args:
                args = []
            names2 = self.search(domain+args, limit=limit).name_get()
        # Merge both results
        return list(set(names2) | set(names1))[:limit]

    @api.multi
    def name_get(self):
        """ Asegura que si hay referencia de plantilla la usa """
        results = super(ProductProduct, self).name_get()
        self.read(['name','product_tmpl_id'], load=False)
        for index, product in enumerate(self):
            if product.product_tmpl_id.ref_template:
                referencia = product.product_tmpl_id.ref_template_name
                # Como tienen plantillas cuyo atributo no es el mismo que el de 
                # las variantes aunque se llamen igual.
                # No hacemos este filtro y cogemos los nombres del atributo
                # directamente
                # variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
                variable_attributes = product.attribute_value_ids.\
                    mapped('attribute_id')
                variant = product.attribute_value_ids._variant_name(
                    variable_attributes)
                if variant:
                    results[index] = (product.id, '[%s (%s)] %s' % (referencia, variant, product.name))
                else:
                    results[index] = (product.id, '[%s] %s' % (referencia, product.name))
        return results
