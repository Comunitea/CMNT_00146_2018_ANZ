# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api, _
from odoo.http import request
from odoo.exceptions import ValidationError

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


class ProductAttributeLine(models.Model):

    _inherit = 'product.attribute.line'

    @api.constrains('atribute_id', 'value_ids')
    def _check_num_values(self):
        for line in self:
            if line.attribute_id.feature and len(line.value_ids) > 1:
                raise ValidationError(
            _('Many values for attribute beacause is product feature'))


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
    new_att_id = fields.Many2one('product.attribute', 'New Att')
    feature = fields.Boolean("Product Feauture")

    @api.multi
    def write(self, vals):
        if vals.get('feature', False):
            vals.update(create_variant=True)
        return super().write(vals)

    @api.model
    def create(self, vals):
        if vals.get('feature', False):
            vals.update(create_variant=True)
        return super().write(vals)

    # @api.multi
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         if record.product_brand_id:
    #             new_name = '{}: {}'.format(record.product_brand_id.name, record.name)
    #         else:
    #             new_name = record.name
    #         if record.product_type_id:
    #             new_name = '{} / {}'.format(new_name, record.product_type_id.value)
    #         if record.product_gender_id:
    #             new_name = '{} / {}'.format(new_name, record.product_gender_id.value)
    #         if record.product_age_id:
    #             new_name = '{} / {}'.format(new_name, record.product_age_id.value)
    #         res.append((record.id, new_name))
    #     return res

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
    product_type_id = fields.Many2one('product.attribute.tag', 'Tipo de producto', required=0)
    product_gender_id = fields.Many2one('product.attribute.tag', 'Género',)
    product_age_id = fields.Many2one('product.attribute.tag', 'Edad',)
    count_line_ids = fields.Integer('Valores', compute=_get_count_line_ids)

    def open_form_view_att(self):
        self.ensure_one()
        view = self.env.ref(
            'product.product_attribute_view_form'
        )
        return {
            'name': _('Attribute'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }


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
    range_search = fields.Text('Range Search')

    def open_form_view_value(self):
        self.ensure_one()
        view = self.env.ref(
            'product_custom_anz.attribute_value_form_view'
        )
        return {
            'name': _('Values'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

    #price_extra = fields.Float(company_dependent=True)
