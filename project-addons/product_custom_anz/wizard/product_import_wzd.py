
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


class ProductImportWzd(models.TransientModel):

    _name = 'product.import.wzd'

    name = fields.Char('Importation name', required=True)
    file = fields.Binary(string='File', required=True)
    filename = fields.Char(string='Filename')

    def _parse_row_vals(self, row, idx):
        res = {
            'code_temp': row[0],
            'name_temp': row[1],
            'name_color': row[2],
            'name_extra': row[3],
            'attr_name': row[4],
            'attr_val': row[5],
            'ean': row[6],
            'code_attr': row[7]
        }

        # Check mandatory values setted
        if not (row[0] and row[1] and row[2] and row[4] and row[5]):
            raise UserError(
                _('The row %s is missing some mandatory column') % str(idx))
        return res

    def _create_xml_id(self, xml_id, res_id, model):
        virual_module_name = 'PT' if model == 'product.template' else 'PP'
        self._cr.execute(
            'INSERT INTO ir_model_data (module, name, res_id, model) \
            VALUES (%s, %s, %s, %s)',
                        (virual_module_name, xml_id, res_id, model))

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

    def _get_attr_value(self, row_vals, idx):
        """
        Get an Existing attribute or raise an error
        """
        domain = [('name', '=', row_vals['attr_name'])]
        attr = self.env['product.attribute'].search(domain)
        if not attr:
            raise UserError(
                _('Error getting attribute %s in line %s: \
                   Not found') % (row_vals['attr_name'], str(idx)))

        domain = [
            ('attribute_id', '=', attr.id),
            ('name', '=', row_vals['attr_val'])
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

    def create_variant(self, template, row_vals, idx):
        # import ipdb; ipdb.set_trace()
        pp_pool = self.env['product.product']

        product_name = row_vals['name_temp'] + ' ' + row_vals['name_color'] + \
            row_vals['name_extra']

        attr_value = self._get_attr_value(row_vals, idx)
        code_attr = str(int(row_vals['code_attr'])) or str(attr_value.id)
        default_code = row_vals['code_temp'] + '-' + code_attr

        # CREATE PRODUCT
        vals = {
            'name': product_name,
            'default_code': default_code,
            'available_in_pos': False,
            'attribute_value_ids': [(4, attr_value.id)],
            'barcode': row_vals['ean'],
            'importation_name': self.name
        }
        if template:
            vals.update(product_tmpl_id=template.id)
        product = pp_pool.create(vals)

        # CREATE PRODUCT XMLID
        self._create_xml_id(
            product.default_code, product.id, 'product.product')

        # WRITE TEMPLATE REF AND XMLID TO THE NEW CREATED TEMPLATE
        if not template:
            template = product.product_tmpl_id
            template.write({
                'ref_template': row_vals['code_temp'],
                'importation_name': self.name
            })

            xml_id = row_vals['code_temp']
            self._create_xml_id(xml_id, template.id, 'product.template')
            template_ids.append(template.id)

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
