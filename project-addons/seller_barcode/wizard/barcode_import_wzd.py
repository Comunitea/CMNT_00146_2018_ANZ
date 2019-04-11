
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


class BarcodeImportWzd(models.TransientModel):

    _name = 'barcode.import.wzd'

    name = fields.Char('Importation name', required=True)
    file = fields.Binary(string='File', required=True)
    brand_id = fields.Many2one('product.brand', 'Brand', required=True)
    partner_id = fields.Many2one('res.partner', 'Seller', required=True, domain=[('seller', '=', True)])
    filename = fields.Char(string='Filename')
    categ_id = fields.Many2one('product.category','Default product category')
    create_attributes = fields.Boolean('Create attributes/values if neccesary', default=True)
    tag_id = fields.Many2one('product.tag')

    def _parse_row_vals(self, row, idx):
        res = {
            'code_temp': row[0], ## Referencia de la plantilla (sin espacios)
            'name_temp': row[1], ## Nombre de la plantilla
            'desc_temp': row[2],  ## Descripcion de la plantilla
            'name_color': row[3], ## Nombre del color
            'name_extra': row[4], ## Nombre extra
            'pvp': row[5] or 0.0, ## COST
            'cost': row[6] or 0.0, ## PVP
            'category': row[7], ## category_name
            'tags': row[8], ## tags separadas por coma
            'image': row[9],
            'age': row[10],  ## Nombre del attributo
            'gender': row[11],  ## Nombre del attributo
            'attr_name': row[12],  ## Nombre del attributo

            'ean': row[13], ##EAN
            'code_barcode': row[14], ## Internal ref del barcode
            'attr_val': row[15], ## Nombre del valor del atributo
            'attr_code': row[16], ##codigo del attributo si lo tiene,
            'barcode_name': row[17], ##nombre del codigo si es distinto y no quiero forzarlo
        }
        # Check mandatory values setted
        if not (row[0] and row[1] and row[2] and row[4] and row[5] and row[6]):
            raise UserError(
                _('The row %s is missing some mandatory column') % str(idx))
        return res

    def _get_color(self, color):
        domain = [('is_color', '=', True), ('name', '=', color)]
        attr_value = self.env['product.attribute.value'].search(domain)
        return attr_value or False

    def _get_age_id(self, age, idx):
        domain = [('code', '=', age)]
        age_id = self.env['product.barcode.age'].search(domain, limit=1)
        if not age_id:
            vals = {'name': age, 'code': age, 'brand_id': self.brand_id.id}
            age_id = self.env['product.barcode.age'].create(vals)
        return age_id

    def _get_gender_id(self, gender, idx):
        domain = [('code', '=', gender)]
        gender_id = self.env['product.barcode.gender'].search(domain, limit=1)
        if not gender_id:
            vals = {'name': gender, 'code': gender, 'brand_id': self.brand_id.id}
            gender_id = self.env['product.barcode.gender'].create(vals)
        return gender_id


    def create_template(self, row, idx):
        name = row['name_temp']
        ref = row['code_temp']
        description =  row['name_temp'] + ' ' + row ['name_extra'] + row['name_color']
        brand_id = self.brand_id.id
        seller_id = self.partner_id.id
        tag = row['tags']
        tag_ids = [(6, 0, self._get_tag_ids(tag).ids)]
        cost = row['cost']
        pvp=row['pvp']
        category = self._get_category_id(row['category'], idx)
        age = self._get_age_id(row['age'], idx)
        gender = self._get_gender_id(row['gender'], idx)
        vals = {'name': name,
                'ref': ref,
                'description': description,
                'brand_id': brand_id.id,
                'seller_id': seller_id.id,
                'tag_ids': tag_ids,
                'cost': cost,
                'pvp': pvp,
                'age': age.id,
                'gender': gender.id,
                'category_id': category.id}
        template = self.env['seller.barcode.template'].create(vals)
        self._create_xml_id(
            ref, template.id, 'seller.barcode.template')
        return template


    def _create_xml_id(self, xml_id, res_id, model):
        virual_module_name = 'SBT' if model == 'seller.barcode.template' else 'SB'
        self._cr.execute(
            'INSERT INTO ir_model_data (module, name, res_id, model) \
            VALUES (%s, %s, %s, %s)',
                        (virual_module_name, xml_id, res_id, model))


    def _get_tag_ids(self, tags_str = ''):
        tags = tags_str.split(',')
        tag_ids = []
        for tag in tags:
            new_tag = self.env['product.tag'].search([('name', '=', tag)], limit=1)
            if not new_tag:
                new_tag = self.env['barcode.tag'].search([('name', '=', tag)], limit=1)
                if new_tag:
                    new_tag = new_tag.tag_id
            if not new_tag:
                vals = {'name': tag, 'tag_id': self.tag_id.id}
                new_tag = self.env['barcode.tag'].create(vals)
            if new_tag:
                tag_ids.append(new_tag)

        return tag_ids

    def _get_category_id(self, category_name = False, idx=0):
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
        xml_id = 'SBT.' + row_vals['code_temp']
        try:
            res = self.env.ref(xml_id)
        except ValueError:
            res = False
        return res

    def _get_attr_value(self, row_vals, idx, categ_id):
        """
        Get an Existing attribute or raise an error
        """
        if not categ_id:
            categ_id = self._get_category_id(row_vals['category'], idx)
        domain = [('attribute_category_id', '=', categ_id.id), ('product_brand_id', '=', self.brand_id.id), ('name', '=', row_vals['attr_name'])]
        attr = self.env['product.attribute'].search(domain)
        if not attr:
            if self.create_attributes:
                vals = {'attribute_category_id': categ_id.id, 'product_brand_id': self.brand_id.id, 'name': row_vals['attr_name']}
                attr = self.env['product.attribute'].create(vals)
            else:
                raise UserError(
                    _('Error getting attribute %s in line %s: \
                       Not found') % (row_vals['attr_name'], str(idx)))
        domain = [
            ('attribute_id', '=', attr.id),
            '|', ('supplier_code', '=', row_vals['code_attr']), ('name', '=', row_vals['attr_val'])
        ]
        attr_value = self.env['product.attribute.value'].search(domain)
        if not attr_value:
            if self.create_attributes:
                vals = {'attribute_id': attr.id,
                        'name': row_vals['attr_val'],
                        'supplier_code': row_vals['code_attr'] or row_vals['attr_val']}
                attr_value = self.env['product.attribute.value'].create(vals)
            else:
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



    def create_variant(self, template, row_vals, idx):
        pp_pool = self.env['seller.barcode']

        product_name = row_vals['name_temp'] + ' ' + row_vals['name_color'] + row_vals['name_extra']
        categ_id = self._get_category_id(row_vals['category'], idx)
        attr_value = self._get_attr_value(row_vals, idx, categ_id)

        code_attr =  row_vals['code_attr'] and str(int(row_vals['code_attr'])) or '%d'%(attr_value.code) or '%04d'%(attr_value.id)
        default_code = row_vals['code_barcode'] or (row_vals['code_temp'] + '.' + code_attr)

        if not template:
            template = self.create_barcode_template(row_vals)

        print ("{} >> Creo {}: referencia: {}. Talla {}. Pvp: {}€".format(idx, product_name, default_code, attr_value.display_name, row_vals['pvp']))
        # CREATE BARCODE
        vals = {
            'barcode': row_vals['ean'],
            'ref': default_code,
            'attribute_value_id': attr_value.id,
            'attribute_value_name': attr_value.name,
            'template_id': template.id

        }

        product = pp_pool.create(vals)
        self._create_xml_id(default_code, product.id, 'seller.barcode')
        return product

    def import_products(self):
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
            if row_vals['code_temp'] == "":
                break
            # If existing template, fail, only templates created from this file
            template = self._get_existing_template_obj(row_vals)
            if template and template.id not in template_ids:
                raise UserError(
                    _('The template %s already exists') % template.name)
            if not template:
                template = self.create_template(row_vals, idx)

            product = self.create_variant(template, row_vals, idx)
            created_product_ids.append(product.id)
            _logger.info(_('IMPORTED PRODUCT %s / %s') % (idx, sh.nrows - 1))

        return self.action_view_products(created_product_ids)

    def action_view_products(self, product_ids):
        self.ensure_one()
        action = self.env.ref(
            'product.product_normal_action_sell').read()[0]
        action['domain'] = [('id', 'in', product_ids)]
        return action
