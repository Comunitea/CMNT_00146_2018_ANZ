# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models, fields, _
from odoo.exceptions import UserError
import xlrd
import base64

import logging
_logger = logging.getLogger(__name__)

# Global variable to store the new created templates
template_ids = []


class MergeValuetWzd(models.TransientModel):

    _name = 'merge.value.wzd'

    @api.model
    def default_get(self, fields):
        record_ids = self._context.get('active_ids')
        res = super().default_get(fields)
        if record_ids and 'map_value_ids' in fields:
            value_ids = self.env['product.attribute.value'].browse(record_ids)
            if len(value_ids.mapped('attribute_id')) > 1:
                raise UserError(_('You try to merge values of two or more \
                    attributes. Please, select values of single attribute'))
            res['map_value_ids'] = value_ids.ids
        return res

    value_id = fields.Many2one('product.attribute.value', 'Merge with value',
                               required=False)
    map_value_ids = fields.Many2many('product.attribute.value',
                                     'merge_values_rel',
                                     'merge_id', 'value_id',
                                     string='Values to merge',
                                     readonly=True)

    @api.multi
    def merge_values(self):
        self.ensure_one()
        _logger.info(_('MERGING ATTRIBUTES VALUES'))
        value = self.value_id
        to_delete_values = self.env['product.attribute.value']
        for value2map in self.map_value_ids:
            if value2map.id == value.id:
                continue

            # Actualizo m2m productos y valores
            query_product_values = """
            UPDATE product_attribute_value_product_product_rel
            SET product_attribute_value_id = %s
            WHERE product_attribute_value_id = %s
            """ % (value.id, value2map.id)

            self._cr.execute(query_product_values)

            # Actualizo m2m líneas de atributo y valores
            query_att_line_values = """
            UPDATE product_attribute_line_product_attribute_value_rel
            SET product_attribute_value_id = %s
            WHERE product_attribute_value_id = %s
            """ % (value.id, value2map.id)
            self._cr.execute(query_att_line_values)

            to_delete_values += value2map

        _logger.info(_('DELETING ATTRIBUTES VALUES'))
        to_delete_values.unlink()
        return
