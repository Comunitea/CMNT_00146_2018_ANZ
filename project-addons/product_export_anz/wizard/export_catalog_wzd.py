
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class ExportCatalogtWzd(models.TransientModel):

    _name = 'export.catalog.wzd'

    scheduled_id = fields.Many2one('scheduled.sale', string='Scheduled')
    brand_id = fields.Many2one('product.brand', string='Brand')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')

    def get_variant_sales(self, variant):
        domain = [
            ('order_id.state', 'in', ['sale', 'done']),
            ('product_id', '=', variant.id),
        ]
        if self.date_start:
            domain.append(('order_id.date_order', '>=', self.date_start))
        if self.date_end:
            domain.append(('order_id.date_order', '<=', self.date_end))

        lines = self.env['sale.order.line'].search(domain)
        res = 0
        for l in lines:
            res += l.product_uom_qty
        return res

    def get_variant_stock_info(self, variant):
        ctx = self._context.copy()
        ctx.update({
            'from_date': self.date_start,
            'to_date': self.date_end,
        })
        res = variant.with_context(ctx).read(['incoming_qty', 'qty_available'])
        return res[0]

    def get_templates(self):
        tmp_pool = self.env['product.template']
        templates = tmp_pool
        if self.scheduled_id:
            templates = self.scheduled_id.product_ids.mapped('product_tmpl_id')
        elif self.brand_id:
            templates = tmp_pool.search([
                    ('product_brand_id', '=', self.brand_id.id),
                ])

        return templates

    def get_report_vals(self):
        res = {}
        templates = self.get_templates()

        if not templates:
            raise UserError(_('No templates founded to export'))

        domain = [
            ('product_tmpl_id', 'in', templates.ids)
        ]
        all_variants = self.env['product.product'].search(domain)
        stock_info = all_variants._compute_quantities_dict(
            False, False, False,
            from_date=self.date_start, to_date=self.date_end)

        idx = 0
        tot = len(templates)
        for tmp in templates:
            idx += 1
            _logger.info("Export template %s / %s" % (str(idx), str(tot)))
            res[tmp.name] = {
                'image': tmp.image_medium or False,
                'cost': tmp.standard_price,
                'pvp': tmp.pvp or tmp.list_price,
                'attr_names': [],
                'sales': [],
                'incomings': [],
                'stocks': [],
            }

            for variant in tmp.product_variant_ids:
                attr_name = ''
                if variant.attribute_value_ids:
                    attr_name = variant.attribute_value_ids[0].name
                res[tmp.name]['attr_names'].append(attr_name)

                sales = self.get_variant_sales(variant)
                res[tmp.name]['sales'].append(sales)

                incomings = stock_info[variant.id]['incoming_qty']
                res[tmp.name]['incomings'].append(incomings)

                stocks = stock_info[variant.id]['qty_available']
                res[tmp.name]['stocks'].append(stocks)

        return res

    def export_catalog_xls(self):
        self.ensure_one()
        data_dic = {
            'brand_id': self.brand_id.id,
            'brand_name': self.brand_id.name,
            'date_start': self.date_start,
            'date_end': self.date_start,
        }
        report_vals = self.get_report_vals()
        data_dic.update(report_vals=report_vals)
        if self._context.get('xls_export'):
            return self.env.ref('product_export_anz.export_catalog_xlsx').\
                report_action(self, data=data_dic)
