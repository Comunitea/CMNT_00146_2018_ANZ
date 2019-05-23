# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# TODO  PLANTILLA:
# ref_template
# ref_template_color
# !!! estas dos columnas son clave y determinan product_template y PT.XXXXXX YYY cuando es posible
# marca - se crea como atributo y como caracteristica de atributo
# color general - amazon, hace falta una especie de "color general"
# composicion de colores - amazon separados por coma o / todos los colores que tiene, se pasa a atributos
# name - Auto explicativo NOT NULL
# categoria NOT NULL -- ver si la metemos a palo seco
# ATRIBUTOS - TODO preguntar a kiko cual era la lógica de esto, por que no recuerdo porque habia tipo y nombre
# Esto se duplicai en atributo y COMO atributo para facilitar el trabajo a los de front
# nombre de talla NOT NULL
# tipo de product - T-Shirt sandalias y eso
# <!-- Marca, puesto arriba -->
# Genero - Puede ser falso?
# edad - puede ser falso?
# DESCRIPCIONES
# descripcion corta
# descripcion larga
# ESPECIFICO por product_product
# coste NOT NULL
# precio de venta NOT NULL - Si es distinto para alguno cambiar
# valor de la talla - 46,47,etc NOT NULL
# supplier name - amazon, esto es un campo que vamos aprovechar para crear ls relaciones entre las tallas
# EAN NOT NULL
# Campos de longitud VARIABLE, pueden aparecer 30 y no son obligatorios
# Si el nombre del campo es tag se busca una etuiqueta
# si el nombre del campo es attribute, se busca un atributo
# TODO vista para ver errorres o devolver resultados

from odoo import api, models, fields, _
from odoo.exceptions import UserError
import xlrd
import base64

import logging
_logger = logging.getLogger(__name__)

# Global variable to store the new created templates
template_ids = []

class ProductImportWzd(models.TransientModel):

    _name = 'product.import.wzd'

    name = fields.Char('Importation name', required=True)
    file = fields.Binary(string='File', required=True)
    filename = fields.Char(string='Filename')

    brand_id = fields.Many2one('product.brand', 'Brand')
    categ_id = fields.Many2one('product.category', 'Default product category')
    create_attributes = fields.Boolean('Create attributes/values if neccesary')

    def _get_brand(self, name, create=False):
        if name:
            brand = self.env['product.brand'].search([('name','=ilike',name)])
            brand.ensure_one()
            return brand
        return self.brand_id

    @api.onchange('file')
    def onchange_filename(self):
        if not self.name and self.filename:
            self.name = self.filename and self.filename.split('.')[0]

    def _parse_rows(self):
        pass

    def _parse_row_vals(self, row, idx):
        res = {
            'code_temp': row[0],
            'name_temp': row[1],
            'name_color': row[2],
            'name_extra': row[3],
            'attr_name': row[4],
            'brand_id': row[5],
            'attr_val': row[6],
            'ean': row[7],
            'code_attr': row[8],
            'cost': row[9] or 0.0,
            'pvp': row[10] or 0.0,
            'category': row[11],
            'type': row[12],
            'gender': row[13],
            'age': row[14],
            'color': row[15],
            'ecommerce':row[16],
            'description':row[17],
            'tag1': row[18],
            'tag2': row[19],
            'tag3': row[20],
        }

        # Check mandatory values setted
        if not row[6]:
            raise UserError(
                _('Missing EAN in row %s ') % str(idx))
        if not (row[0] and row[1] and row[2] and row[4] and row[6]):
            raise UserError(
                _('The row %s is missing some mandatory column') % str(idx))
        if not self._get_brand(row[5]):
            raise UserError(
                _('The row %s is missing brand') % str(idx))
        return res

    def _create_xml_id(self, xml_id, res_id, model):
        virual_module_name = 'PT' if model == 'product.template' else 'PP'
        self._cr.execute(
            'INSERT INTO ir_model_data (module, name, res_id, model) \
            VALUES (%s, %s, %s, %s)',
                        (virual_module_name, xml_id, res_id, model))


    def _get_category_id(self, category_name = False, idx=0):
        categ_id = False
        if category_name:
            categ_id = self.env['product.category'].search([('name', '=', category_name)], limit=1)

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


    def _get_product_att(self, value, brand_id, type='type', create=False):
        at_tag = self.env['product.attribute.tag']
        domain = [('product_brand_id', '=', brand_id), ('type', '=', type), ('value', '=', value)]
        tag = at_tag.search(domain, limit=1)
        if not tag and create:
            vals ={'product_brand_id': brand_id,
                   'type': type,
                   'value': value}

            tag = at_tag.create(vals)
            print ("Se ha creado la etiqueta de atributo: {}".format(tag.display_name))
        return tag


    def _get_attr_value(self, row_vals, idx, categ_id):
        """
        Get an Existing attribute or raise an error
        """
        if not categ_id:
            categ_id = self._get_category_id(row_vals['category'], idx)

        domain = [('product_brand_id', '=', self._get_brand(row_vals['brand_id']).id)]
        tag_type_id=tag_age_id=tag_gender_id=False
        if row_vals['type']:
            tag_type_id = self._get_product_att(row_vals['type'], self._get_brand(row_vals['brand_id']).id, 'type', self.create_attributes)
            if tag_type_id:
                domain += [('product_type_id', '=', tag_type_id.id)]
            else:
                domain += [('product_type_id', '=', False)]

        if row_vals['gender']:
            tag_gender_id = self._get_product_att(row_vals['gender'], self._get_brand(row_vals['brand_id']).id,'gender', self.create_attributes)
            if tag_gender_id:
                domain += [('product_gender_id', '=', tag_gender_id.id)]
            else:
                domain += [('product_gender_id', '=', False)]

        if row_vals['age']:
            tag_age_id = self._get_product_att(row_vals['age'], self._get_brand(row_vals['brand_id']).id,'age', self.create_attributes)
            if tag_age_id:
                domain += [('product_age_id', '=', tag_age_id.id)]
            else:
                domain += [('product_age_id', '=', False)]
        print (domain)
        attr = self.env['product.attribute'].search(domain, limit=1)
        if not attr:
            if self.create_attributes:
                vals = {#'attribute_category_id': categ_id.id,
                        'product_brand_id': self._get_brand(row_vals['brand_id']).id,
                        'name': row_vals['attr_name'],
                        'product_type_id': tag_type_id and tag_type_id.id,
                        'product_gender_id': tag_gender_id and tag_gender_id.id,
                        'product_age_id': tag_age_id and tag_age_id.id}
                attr = self.env['product.attribute'].create(vals)
                print("Se ha creado el atributo: {}".format(attr.display_name))
            else:
                raise UserError(
                        _('Error: El atributo %s in line %s no existe') % (row_vals['attr_name'], str(idx)))
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
                print("Se ha creado el valor {} para el atributo: {}".format(attr_value.display_name, attr.display_name))
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

    def create_variant(self, template, row_vals, idx):

        pp_pool = self.env['product.product']
        product_name = row_vals['name_temp'] + ' ' + row_vals['name_color'] + row_vals['name_extra']
        categ_id = self._get_category_id(row_vals['category'], idx)
        attr_value = self._get_attr_value(row_vals, idx, categ_id)

        code_attr = attr_value.supplier_code or row_vals['code_attr'] and str(int(row_vals['code_attr'])) or '%04d' % (attr_value.id)
        default_code = row_vals['code_temp'] + '.' + code_attr

        vals = {
            'name': product_name,
            'default_code': default_code,
            'available_in_pos': False,
            'attribute_value_ids': [(4, attr_value.id)],
            'barcode': str(int(row_vals['ean'])),
            'importation_name': self.name,
            'lst_price': row_vals['pvp'],
            'standard_price': row_vals['cost'],
            'type': 'product'
        }
        if template:
            vals.update(product_tmpl_id=template.id)
        product = pp_pool.create(vals)

        # CREATE PRODUCT XMLID
        self._create_xml_id(
            product.barcode, product.id, 'product.product')
        print("Se crea el producto {} con xml_id {} \nVals :{} y ".format(product.display_name, product.get_xml_id(), vals))
        # WRITE TEMPLATE REF AND XMLID TO THE NEW CREATED TEMPLATE
        if not template:
            template = product.product_tmpl_id
            tags = self._get_tags(row_vals)
            vals = {
                'ref_template': row_vals['code_temp'],
                'importation_name': self.name,
                'product_brand_id': self._get_brand(row_vals['brand_id']).id,
                'categ_id': categ_id.id
            }
            if tags:
                vals.update(tag_ids=[(6, 0, tags)])
            template.write(vals)
            xml_id = row_vals['code_temp']
            self._create_xml_id(xml_id, template.id, 'product.template')
            template_ids.append(template.id)
            print("Se crea la plantilla {} con xml_id {} \nVals :{} y ".format(template.display_name, template.get_xml_id(), vals))
            if len(template.product_variant_ids)>1:
                raise UserError(
                    "Linea %s: Plantilla %s. Si la plantilla tiene más de una variante debes de crear variantes y el codigo del atributo debe ser distinto a 'NO'" %(idx, template.display_name))

        # LINK ATTRIBUTE VALUE TO THE TEMPLATE
        self._update_template_attributes(template, attr_value)
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
            if row_vals['code_temp'] == "" or row_vals['code_temp'] == 'FIN' or len(row_vals['code_temp']) < 1:
                break
            # If existing template, fail, only templates created from this file
            template = self._get_existing_template_obj(row_vals)
            if template and template.id not in template_ids:
                raise UserError(
                    _('The template %s already exists') % template.name)

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
