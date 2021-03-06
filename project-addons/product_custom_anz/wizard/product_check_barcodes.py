# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _
from odoo.exceptions import UserError
import xlrd
import base64

import logging

_logger = logging.getLogger(__name__)

# Global variable to store the new created templates
template_ids = []


class ProductCheckBarcodes(models.TransientModel):
    _name = 'product.check.barcodes'

    name = fields.Char('Importation name')
    file = fields.Binary(string='File')
    brand_id = fields.Many2one('product.brand', 'Brand', required=True)
    filename = fields.Char(string='Filename')
    categ_id = fields.Many2one('product.category', 'Default product category')
    create_attributes = fields.Boolean('Create attributes/values if neccesary', default=False)

    def _parse_row_vals(self, row, idx):
        res = {
            'code_temp': row[0],
            'name_temp': row[1],
            'name_color': row[2],
            'name_extra': row[3],
            'attr_name': row[4],
            'attr_val': row[5],
            'ean': row[6],
            'code_attr': row[7],
            'cost': row[8] or 0.0,
            'pvp': row[9] or 0.0,
            'category': row[10],
            'type': row[11],
            'gender': row[12],
            'age': row[13],
            'tag1': row[14],
            'tag2': row[15],
            'tag3': row[16],
        }

        # Check mandatory values setted
        if not row[6]:
            raise UserError(
                _('Missing EAN in row %s ') % str(idx))
        if not (row[0] and row[1] and row[2] and row[4] and row[5]):
            raise UserError(
                _('The row %s is missing some mandatory column') % str(idx))
        return res

    def get_ref(self, ext_id):
        ext_id_c = ext_id.split('.')

        if len(ext_id_c) == 1:
            domain = [('model', '=', 'product.product'), ('module', '=', False), ('name', '=', ext_id)]
        else:
            domain = [('model', '=', 'product.product'), ('module', '=', ext_id_c[0]), ('name', '=', ext_id_c[1])]

        res_id = self.env['ir.model.data'].search(domain, limit=1)
        return res_id and res_id.res_id or False

    def _delete_xml_id(self, res_id, model):
        self._cr.execute(
            "delete from ir_model_data where model = '{}' and res_id = {}".format(model, res_id))

    def _create_xml_id(self, xml_id, res_id, model):
        virual_module_name = 'PT' if model == 'product.template' else 'PP'
        self._cr.execute(
            'INSERT INTO ir_model_data (module, name, res_id, model) \
            VALUES (%s, %s, %s, %s)',
            (virual_module_name, xml_id, res_id, model))

    def _get_category_id(self, category_name=False, idx=0):
        categ_id = False
        if category_name:
            categ_id = self.env['product.category'].search([('name', '=', category_name)])

        categ_id = categ_id or self.categ_id
        if not categ_id:
            raise UserError(
                _('The row %s has wrong category (%s) and not default category') % (str(idx), category_name))
        return categ_id

    def _get_existing_template_obj(self, row_vals):
        """
        Get an existing template by xml id or return false
        """
        res = False
        xml_id = 'PT.' + row_vals['code_temp']
        try:
            res = self.env.ref(xml_id)
        except ValueError:
            res = False
        return res

    def _get_product_att(self, value, type='type', create=False):
        at_tag = self.env['product.attribute.tag']
        domain = [('product_brand_id', '=', self.brand_id.id), ('type', '=', type), ('value', '=', value)]
        tag = at_tag.search(domain, limit=1)
        if not tag and create:
            vals = {'product_brand_id': self.brand_id.id,
                    'type': type,
                    'value': value}

            tag = at_tag.create(vals)
            print("Se ha creado la etiqueta de atributo: {}".format(tag.display_name))
        return tag

    def _get_attr_value(self, row_vals, idx, categ_id):
        """
        Get an Existing attribute or raise an error
        """

        #if not categ_id:
        #    categ_id = self._get_category_id(row_vals['category'], idx)

        domain = [('product_brand_id', '=', self.brand_id.id)]
        tag_type_id = tag_age_id = tag_gender_id = False
        if row_vals['type']:
            tag_type_id = self._get_product_att(row_vals['type'], 'type', False)
            if tag_type_id:
                domain += [('product_type_id', '=', tag_type_id.id)]
            else:
                domain += [('product_type_id', '=', False)]

        if row_vals['gender']:
            tag_gender_id = self._get_product_att(row_vals['gender'], 'gender', False)
            if tag_gender_id:
                domain += [('product_gender_id', '=', tag_gender_id.id)]
            else:
                domain += [('product_gender_id', '=', False)]

        if row_vals['age']:
            tag_age_id = self._get_product_att(row_vals['age'], 'age', False)
            if tag_age_id:
                domain += [('product_age_id', '=', tag_age_id.id)]
            else:
                domain += [('product_age_id', '=', False)]
        print(domain)
        attr = self.env['product.attribute'].search(domain, limit=1)
        if not attr:

            raise UserError(
                _('Error getting attribute %s in line %s: \
                   Not found') % (row_vals['attr_name'], str(idx)))
        domain = [
            ('attribute_id', '=', attr.id),
            '|', ('supplier_code', '=', row_vals['code_attr']), ('name', '=', row_vals['attr_val'])
        ]
        attr_value = self.env['product.attribute.value'].search(domain)
        if not attr_value:
            raise UserError(
                _('Error getting attribute %s with value %s in line %s: \
                    Not found') % (attr.name, row_vals['attr_val'], str(idx)))
        return attr_value

    def _update_template_attributes(self, template, attr_value):
        """
        Add to the template a new attribute value
        """
        pal = self.env['product.attribute.line']

        domain = [
            ('product_tmpl_id', '=', template.id),
            ('attribute_id', '=', attr_value.attribute_id.id)
        ]
        attr_line = pal.search(domain, limit=1)

        # Create new attr_line
        if not attr_line:
            vals = {
                'attribute_id': attr_value.attribute_id.id,
                'value_ids': [(4, attr_value.id)],
                'product_tmpl_id': template.id
            }
            pal.create(vals)
        # Add new attr value to the attr line
        else:
            attr_line.write({'value_ids': [(4, attr_value.id)]})

    def _get_tags(self, vals):

        def find_tag(tag):
            domain = [('name', '=', tag)]
            s_t = self.env['product.supplier.tag'].search(domain, limit=1)
            if s_t:
                return s_t.tag_id
            return self.env['product.tag'].search(domain, limit=1)

        tag_ids = []
        tag = find_tag(vals['tag1'])
        if tag:
            tag_ids.append(tag.id)

        tag = find_tag(vals['tag2'])
        if tag:
            tag_ids.append(tag.id)

        tag = find_tag(vals['tag3'])

        if tag:
            tag_ids.append(tag.id)
        return tag_ids

    def act_barcodes(self, template, row_vals, idx):

        pp_pool = self.env['product.product']
        product_name = row_vals['name_temp'] + ' ' + row_vals['name_color'] + row_vals['name_extra']
        #categ_id = self._get_category_id(row_vals['category'], idx)
        attr_value = self._get_attr_value(row_vals, idx, False)
        code_attr = row_vals['code_attr'] and str(int(row_vals['code_attr'])) or '%04d' % (attr_value.id)
        default_code = row_vals['code_temp'] + '.' + code_attr

        print("{} >> Creo {}: referencia: {}. Talla {}. Pvp: {}€".format(idx, product_name, default_code,
                                                                         attr_value.display_name, row_vals['pvp']))
        try:
            ean13 = str(int(row_vals['ean']))
        except:
            ean13 = ''

        # CREATE PRODUCT
        vals = {
            'name': product_name,
            'default_code': default_code,
            'available_in_pos': False,
            'attribute_value_ids': [(4, attr_value.id)],
            'barcode': ean13,
            'importation_name': self.name,
            'lst_price': row_vals['pvp'],
            'standard_price': row_vals['cost'],
            'type': 'product',

        }
        #if template:
        #    vals.update(product_tmpl_id=template.id)

        # En vez de crear el producto
        domain = [('default_code', '=', default_code)]
        product = self.env['product.product'].search(domain, limit=1)
        if not product:
            domain += [('active', '=', False)]
            product = self.env['product.product'].search(domain, limit=1)
        if product:
            # Borro el xml antiguo
            self._delete_xml_id(product.id, 'product.product')
            # CREATE PRODUCT XMLID
            self._create_xml_id(ean13, product.id, 'product.product')
            product.barcode = ean13
        return product

    def check_barcodes(self):
        self.ensure_one()
        _logger.info(_('STARTING PRODUCT IMPORTATION'))

        # get the first worksheet
        file = base64.b64decode(self.file)
        book = xlrd.open_workbook(file_contents=file)
        sh = book.sheet_by_index(0)
        created_product_ids = []
        idx = 1
        for nline in range(1, sh.nrows):

            idx += 1
            row = sh.row_values(nline)
            row_vals = self._parse_row_vals(row, idx)
            if row_vals['code_temp'] == "" or row_vals['code_temp'] == 'FIN' or len(row_vals['code_temp']) < 1:
                break
            # If existing template, fail, only templates created from this file
            template = self._get_existing_template_obj(row_vals)
            product = self.act_barcodes(template, row_vals, idx)

            created_product_ids.append(product.id)
            _logger.info(_('IMPORTED PRODUCT %s / %s') % (idx, sh.nrows - 1))

        return self.action_view_products(created_product_ids)

    def action_view_products(self, product_ids):
        self.ensure_one()
        action = self.env.ref(
            'product.product_normal_action_sell').read()[0]
        action['domain'] = [('id', 'in', product_ids)]
        return action
