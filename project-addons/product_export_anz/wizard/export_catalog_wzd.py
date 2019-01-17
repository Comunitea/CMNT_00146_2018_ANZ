
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)

class CatalogType(models.Model):
    _name = 'export.catalog.type'

    name = fields.Char('Name')
    incomings = fields.Boolean('Inputs')
    outgoings = fields.Boolean('Outputs')
    purchases = fields.Boolean('Purchases')
    sales = fields.Boolean('Sales')
    stocks = fields.Boolean('Stocks')
    pvp = fields.Boolean('P.V.P.')
    cost = fields.Boolean('Cpst')
    company_header = fields.Char('Company header')
    image = fields.Boolean('Template Image')
    total = fields.Boolean('Total')
    euros = fields.Boolean('€')
    show_per_cent = fields.Boolean('% en resumen')


class ExportCatalogtWzd(models.TransientModel):

    _name = 'export.catalog.wzd'

    scheduled_id = fields.Many2one('scheduled.sale', string='Scheduled')
    brand_id = fields.Many2one('product.brand', string='Brand')
    categ_id = fields.Many2one('product.category', string='Category')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    catalog_type_id = fields.Many2one('export.catalog.type', 'Catalog type', required=True)
    limit = fields.Integer('Limit', default=50)

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

    def get_variant_purchases(self, variant):
        domain = [
            ('order_id.state', 'in', ['purchase', 'done']),
            ('product_id', '=', variant.id),
        ]
        if self.date_start:
            domain.append(('order_id.date_order', '>=', self.date_start))
        if self.date_end:
            domain.append(('order_id.date_order', '<=', self.date_end))

        lines = self.env['purchase.order.line'].search(domain)
        res = 0
        for l in lines:
            res += l.product_qty
        return res

    def get_variant_stock_info(self, variant):
        ctx = self._context.copy()
        ctx.update({
            'from_date': self.date_start,
            'to_date': self.date_end,
        })
        res = variant.with_context(ctx).read(['incoming_qty', 'qty_available', 'outgoing_qty'])
        return res[0]

    def get_templates(self):
        tmp_pool = self.env['product.template']
        templates = tmp_pool
        domain = []
        if self.scheduled_id:
            domain += [('scheduled_sale_id', '=', self.scheduled_id.id)]
        if self.brand_id:
            domain += [('product_brand_id', '=', self.brand_id.id)]
        if self.categ_id:
            domain += [('categ_id', '=', self.categ_id.id)]

        templates = tmp_pool.search(domain, limit = self.limit)
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
                #'image': tmp.image_medium or False,
                'tmp_id': tmp.id,
                'cost': tmp.standard_price,
                'pvp': tmp.pvp or tmp.list_price,
                'attr_names': [],
                'sales': [],
                'purchases': [],
                'incomings': [],
                'outgoings': [],
                'stocks': [],
                'percent': 0.00,

            }
            sales=purchases=incomings=outgoings=stocks=0
            for variant in tmp.product_variant_ids:
                attr_name = ''
                if variant.attribute_value_ids:
                    attr_name = variant.attribute_value_ids[0].name
                res[tmp.name]['attr_names'].append(attr_name)
                if self.catalog_type_id.sales:
                    sales = self.get_variant_sales(variant)
                    res[tmp.name]['sales'].append(sales)

                if self.catalog_type_id.purchases:
                    purchases = self.get_variant_purchases(variant)
                    res[tmp.name]['purchases'].append(purchases)

                if self.catalog_type_id.incomings:
                    incomings = stock_info[variant.id]['incoming_qty']
                    res[tmp.name]['incomings'].append(incomings)

                if self.catalog_type_id.outgoings:
                    outgoings = stock_info[variant.id]['outgoing_qty']
                    res[tmp.name]['outgoings'].append(outgoings)

                if self.catalog_type_id.stocks:
                    stocks = stock_info[variant.id]['qty_available']
                    res[tmp.name]['stocks'].append(stocks)

                if self.catalog_type_id.show_per_cent:
                    if incomings and outgoings:
                        percent = round(incomings/outgoings * 100, 2)
                    elif purchases and sales:
                        percent = round(sales/purchases * 100, 2)
                    else:
                        percent = 0
                    res[tmp.name]['percent'] = percent


        return res

    def export_catalog_xls(self):
        self.ensure_one()
        data_dic = {
            'wzd_id': self.id
        }
        report_vals = self.get_report_vals()
        #data_dic.update(report_vals=report_vals)
        if self._context.get('xls_export'):
            report = self.env.ref('product_export_anz.export_catalog_xlsx')
            report.file = "{}_{}.xls".format(self.catalog_type_id.name, self.scheduled_id.name or self.brand_id.name or '')
            return report.\
                report_action(self, data=data_dic)
