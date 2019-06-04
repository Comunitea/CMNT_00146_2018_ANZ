# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models,api

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


class ProductAttribute(models.Model):

    _inherit = "product.attribute"

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

    #price_extra = fields.Float(company_dependent=True)


class ProductProduct(models.Model):
    "Eliminar cuando todos los artículos se creen con el importador"
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if len(str(name)) > 2:
            ref_args = self.env['product.product'].search([('product_tmpl_id.ref_template_name',operator,name)]).ids
            if ref_args:
                ref_args = [('id','in',ref_args)]
                args = ['|'] + args + ref_args if args else ref_args
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.multi
    def name_get(self):
        """ Asegura que si hay referencia de plantilla la usa """
        results = super(ProductProduct,self).name_get()
        for index, product in enumerate(self):
            if product.product_tmpl_id.ref_template:
                referencia = product.product_tmpl_id.ref_template_name
                variant = product.attribute_value_ids
                if variant:
                    if variant[0].supplier_code:
                        referencia += '.'+variant[0].supplier_code
                    results[index] = (product.id, '[%s] %s (%s)' % (referencia, product.name, variant[0].name))
                else:
                    results[index] = (product.id, '[%s] %s' % (referencia, product.name))
        return results
