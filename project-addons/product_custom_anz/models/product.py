# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models,api
from odoo.http import request

class ProductAttributeCategory(models.Model):
    _name = 'product.attribute.category'

    name = fields.Char(string='Category')

class ProductAttributeTag(models.Model):

    _name = "product.attribute.tag"

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, '{}: {}'.format(record.product_brand_id.name, record.value)))
        return res
    product_brand_id = fields.Many2one('product.brand', 'Brand', required=1)
    type = fields.Selection([('type', 'Tipo de articulo'), ('gender', 'Género'), ('age', 'Edad')], required=1)
    value = fields.Char('Valor', required=1)
    lines_count = fields.Integer(string='Number of products', compute='_get_attr_lines')

    @api.multi
    def _get_attr_lines(self):
        for tag in self:
            lines = request.env['product.attribute.line'].sudo().search([('attribute_id', '=', tag.id)])
            tag.lines_count = len(lines)


class ProductAttribute(models.Model):

    _inherit = "product.attribute"

    @api.multi
    @api.depends('name', 'product_brand_id', 'product_type_id', 
                 'product_gender_id', 'product_age_id')
    def _get_srch_name(self):
        for att in self:
            att.srch_name = att.display_name

    display_name = fields.Char(store=False, string='Complet Name')
    srch_name = fields.Char(store=True, string='Search Name',
                            compute="_get_srch_name")

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.product_brand_id:
                new_name = '{}: {}'.format(record.product_brand_id.name, record.name)
            else:
                new_name = record.name
            if record.product_type_id:
                new_name = '{} / {}'.format(new_name, record.product_type_id.value)
            if record.product_gender_id:
                new_name = '{} / {}'.format(new_name, record.product_gender_id.value)
            if record.product_age_id:
                new_name = '{} / {}'.format(new_name, record.product_age_id.value)
            res.append((record.id, new_name))
        return res

    @api.multi
    def _get_count_line_ids(self):
        for attr in self:
            attr.count_line_ids = len(attr.value_ids)


    def action_show_attribute_values(self):
        action = self.env.ref('product.variants_action').read()[0]
        action['domain'] = [('attribute_id', '=', self.id)]
        action['context'] = {'default_attribute_id': self.id}
        return action


    is_color = fields.Boolean("Is color",
                              help="Check it if attribute will contain colors")
    is_tboot = fields.Boolean("Is type of boot",
                              help="Check it if attribute will contain \
                              type of boots")

    product_brand_id = fields.Many2one('product.brand', 'Brand')
    attribute_category_id = fields.Many2one('product.category', 'Category')
    product_type_id = fields.Many2one('product.attribute.tag', 'Tipo de producto', required=1)
    product_gender_id = fields.Many2one('product.attribute.tag', 'Género',)
    product_age_id = fields.Many2one('product.attribute.tag', 'Edad',)
    count_line_ids = fields.Integer('Valores', compute=_get_count_line_ids)

class ProductAttributeValue(models.Model):

    _inherit = "product.attribute.value"

    is_color = fields.Boolean("Is color",
                              related="attribute_id.is_color",
                              readonly=True)
    is_tboot = fields.Boolean("Is type of boot",
                              related="attribute_id.is_tboot",
                              readonly=True)
    supplier_code = fields.Char("Supplier name")
    name_normalizado = fields.Char()
    attr_name = fields.Char('Attribute', related="attribute_id.srch_name")

    #price_extra = fields.Float(company_dependent=True)


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
