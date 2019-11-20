# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ShippingCustomCustomerAnz(models.AbstractModel):
    _name = 'report.stock.report_picking'

    def get_report_values(self, docids, data=None):
        #import ipdb; ipdb.set_trace()
        model = 'stock.picking'
        doc_id = self.env[model].browse(docids)

        code = doc_id.picking_type_id.code
        if code != 'incoming':
            sorted_lines = doc_id.move_line_ids.sorted(key=lambda m: m.location_id.sequence)
        else:
            sorted_lines = doc_id.move_line_ids.sorted(key=lambda m: m.location_dest_id.sequence)
        docargs = {
           'doc_ids': docids,
           'doc_model': '',
           'docs': doc_id,
           'ordered_lines': sorted_lines
        }
        return docargs