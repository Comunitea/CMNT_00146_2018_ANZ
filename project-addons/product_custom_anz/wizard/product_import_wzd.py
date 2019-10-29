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

    def _get_brand(self, name, create=False):
        if name:
            brand = self.env['product.brand'].search(
                [('name', '=ilike', name)])
            brand.ensure_one()
            return brand
        return self.brand_id

    @api.onchange('file')
    def onchange_filename(self):
        if not self.name and self.filename:
            self.name = self.filename and self.filename.split('.')[0]

    def _parse_row_vals(self, row, idx):
        res = {
            'code_temp': str(row[0]),
            'name_temp': str(row[1]),
            'name_color': str(row[2]),
            'name_extra': str(row[3]),
            'attr_name': str(row[4]),
            'brand_id': str(row[5]),
            'attr_val': str(row[6]),
            'ean': str(row[7]),
            'code_attr': str(row[8]),
            'cost': row[9] or 0.0,
            'pvp': row[10] or 0.0,
            'category': str(row[11]),
            'type': str(row[12]),
            'gender': str(row[13]),
            'age': str(row[14]),
            'color': str(row[15]),
            'ecommerce': str(row[16]),
            'description': str(row[17]),
            'tag1': str(row[18]),
            'tag2': str(row[19]),
            'tag3': str(row[20]),
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

    def _get_category_id(self, category_name=False, idx=0):
        categ_id = False
        if category_name:
            categ_id = self.env['product.category'].search(
                [('name', '=', category_name)], limit=1)

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

    def _get_attribute(self, attr_name):
        domain = [('name', '=', attr_name)]
        attr = self.env['product.attribute'].search(domain, limit=1)
        return attr

    def _get_attr_value(self, attr_name, attr_val, idx):
        """
        Busco el valor de atributo, si no existe atributo o valor fallo
        """
        # BUSCO EL ATRIBUTO
        attr = self._get_attribute(attr_name)
        if not attr:
            raise UserError(
                _('Error: El atributo %s in line %s no existe') %
                (attr_name, str(idx)))

        # BUSCO EL VALOR DE ESE ATRIBUTO
        domain = [
            ('attribute_id', '=', attr.id),
            ('name', '=', attr_val)
        ]
        attr_value = self.env['product.attribute.value'].search(domain)
        if not attr_value:
            raise UserError(
                _('Error getting attribute %s with value %s in line %s: \
                    Not found') % (attr.name, attr_val, str(idx)))
        return attr_value

    def _get_extra_attr_value(self, row_vals, idx):
        """
        Si hay columna para tipo genero o edad busco el valor de ese atributo
        si no lo encuenta falla
        """
        extra_attrs = []
        maps = {
            'type': 'TIPO PRODUCTO',
            'gender': 'GÉNERO',
            'age': 'EDAD'
        }
        for key in ['type', 'gender', 'age']:
            attr_name = maps.get(key, False)
            if not attr_name or not row_vals[key]:
                continue
            attr_val = row_vals[key]
            attr_value = self._get_attr_value(attr_name, attr_val, idx)
            extra_attrs.append(attr_value)
        return extra_attrs

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

        pp_pool = self.env['product.product']
        product_name = row_vals['name_temp'] + ' ' + row_vals['name_color'] + row_vals['name_extra']
        categ_id = self._get_category_id(row_vals['category'], idx)

        # Obtengo valor del atributo principal
        attr_value = self._get_attr_value(
            row_vals['attr_name'], row_vals['attr_val'], idx)

        # Calculo los valores de los atributos edad tipo y genero si vienen
        # y los añado al valor del atributo principal
        extra_values = self._get_extra_attr_value(row_vals, idx)
        all_values = [attr_value] + extra_values

        attr_values_lst = []
        if all_values:
            extra_values_lst = [(4, v.id) for v in all_values]
            attr_values_lst.extend(extra_values_lst)

        # Calculo default code
        code_attr = attr_value.supplier_code or row_vals['code_attr'] and \
            row_vals['code_attr'] or '%04d' % (attr_value.id)
        default_code = row_vals['code_temp'] + '.' + code_attr

        # CREO LA VARIANTE
        vals = {
            'name': product_name,
            'default_code': default_code,
            'available_in_pos': False,
            'attribute_value_ids': attr_values_lst,
            'barcode': row_vals['ean'],
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
        print("Se crea el producto {} con xml_id {} \nVals :{} y ".format(
            product.display_name, product.get_xml_id(), vals))

        # WRITE TEMPLATE REF AND XMLID TO THE NEW CREATED TEMPLATE
        if not template:
            template = product.product_tmpl_id
            vals = {
                'ref_template': row_vals['code_temp'],
                'importation_name': self.name,
                'product_brand_id': self._get_brand(row_vals['brand_id']).id,
                'categ_id': categ_id.id
            }
            template.write(vals)
            xml_id = row_vals['code_temp']
            self._create_xml_id(xml_id, template.id, 'product.template')
            template_ids.append(template.id)
            print("Se crea la plantilla {} con xml_id {} \nVals :{} y ".format(
                template.display_name, template.get_xml_id(), vals))
            if len(template.product_variant_ids) > 1:
                raise UserError(
                    "Linea %s: Plantilla %s. Si la plantilla tiene más de una \
                    variante debes de crear variantes y el codigo del \
                    atributo debe ser distinto a 'NO'" %
                    (idx, template.display_name))

        # LINK ATTRIBUTE VALUE TO THE TEMPLATE
        for att_val in all_values:
            self._update_template_attributes(template, att_val)
        return product

    def action_view_products(self, product_ids):
        self.ensure_one()
        action = self.env.ref(
            'product.product_normal_action_sell').read()[0]
        action['domain'] = [('id', 'in', product_ids)]
        return action

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
            if not row_vals['code_temp'] or row_vals['code_temp'] == 'FIN':
                break

            # Si existe plantilla y no fué creada desde el importador error
            template = self._get_existing_template_obj(row_vals)
            if template and template.id not in template_ids:
                raise UserError(
                    _('The template %s already exists') % template.name)

            # CREO LA VARIANTE
            product = self.create_variant(template, row_vals, idx)
            created_product_ids.append(product.id)
            _logger.info(_('IMPORTED PRODUCT %s / %s') % (idx, sh.nrows - 1))
        return self.action_view_products(created_product_ids)
