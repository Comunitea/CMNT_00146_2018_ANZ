# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ShippingCustomCustomerAnz(models.AbstractModel):
    _name = 'report.stock.report_picking'

    def get_report_values(self, docids, data=None):
        model = 'stock.picking'
        doc_id = self.env[model].browse(docids)
        code = doc_id.picking_type_id.code
        if code == 'incoming':
            #sorted_lines = doc_id.move_line_ids.sorted(key=lambda m: (m.location_dest_id.sequence + m.product_id.attribute_value_ids.sequence/1000))
            sorted_lines = doc_id.move_line_ids.sorted(key=lambda m: (m.location_dest_id.sequence, m.product_id.product_tmpl_id, m.product_id.attribute_value_ids.sequence))
        else:
            #sorted_lines = doc_id.move_line_ids.sorted(key=lambda m: (m.location_id.sequence + m.product_id.attribute_value_ids.sequence/1000))
            sorted_lines = doc_id.move_line_ids.sorted(key=lambda m: (
            m.location_id.sequence, m.product_id.product_tmpl_id, m.product_id.attribute_value_ids.sequence))

        template_qty = {}
        for move in sorted_lines:
            template = move.product_id.product_tmpl_id
            str = template.name + move.location_id.name
            qty = move.qty_done if move.state == 'done' else move.product_uom_qty
            if str in template_qty.keys():
                template_qty[str] += qty
            else:
                template_qty.update({str: qty})


        docargs = {
           #'group_by_template': False,
           'doc_ids': docids,
           'doc_model': '',
           'docs': doc_id,
           'sorted_lines': sorted_lines,
           'template_qty': template_qty
        }
        return docargs



class ShippingCustomCustomerAnzGroupTemplate(models.AbstractModel):
    _name = 'report.stock_picking_custom.report_shipping_custom_customer_anz'

    def get_report_values(self, docids, data=None):
        model = 'stock.picking'
        doc_id = self.env[model].browse(docids)
        code = doc_id.picking_type_id.code

        sorted_lines = doc_id.move_line_ids.sorted(key=lambda m: (m.location_dest_id.sequence, m.product_id.product_tmpl_id, m.product_id.attribute_value_ids.sequence))
        template_qty = {}
        lines = []
        templates = {}
        product_ids  = sorted_lines.mapped('product_id')
        template_ids = product_ids.mapped('product_tmpl_id')

        for template in template_ids:
            template_qty = 0
            product_ids = {}
            template_lines = sorted_lines.filtered(lambda x: x.product_id.product_tmpl_id == template)
            index_template = '{}'.format(template.id)
            for move in template_lines:
                qty = move.qty_done if move.state == 'done' else move.product_uom_qty
                index = '{}'.format(move.product_id.id)
                if index in product_ids.keys():
                    product_ids[index]['qty'] += qty
                else:
                    val = {'product_id': move.product_id,
                           'product_tmpl_id': template,
                           'qty': qty,
                           'variant_name': move.product_id.attribute_value_ids.filtered(lambda x:x.attribute_id.create_variant)}
                    val = {index: val}
                    product_ids.update(val)

                template_qty += qty

            p_ids = []
            for index in product_ids.keys():
                p_ids.append(product_ids[index])
            val_template = {'template_id': template,
                            'qty': template_qty,
                            'product_ids': p_ids}

            template_val = {index_template: val_template}
            templates.update(template_val)

        t_ids = []
        for index in templates:
            t_ids.append(templates[index])

        print(t_ids)
        docargs = {
           #'group_by_template': False,
           'doc_ids': docids,
           'doc_model': '',
           'docs': doc_id,
           'sorted_lines': sorted_lines,
           'templates': t_ids
        }
        return docargs

        for move in sorted_lines:
            template = move.product_id.product_tmpl_id
            str = template.name + move.location_dest_id.name
            qty = move.qty_done if move.state == 'done' else move.product_uom_qty
            if str in template_qty.keys():
                template_qty[str] += qty
            else:
                template_qty.update({str: qty})





        docargs = {
           #'group_by_template': False,
           'doc_ids': docids,
           'doc_model': '',
           'docs': doc_id,
           'sorted_lines': sorted_lines,
           'templates': templates
        }
        return docargs