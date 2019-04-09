
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round

import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _compute_move_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):

        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        if to_date and to_date < fields.Datetime.now(): #Only to_date as to_date will correspond to qty_available
            dates_in_the_past = True
        if not to_date:
            to_date = fields.Datetime.now()
        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        domain_move_in_todo = [('state', '=', 'done')] + domain_move_in
        domain_move_out_todo = [('state', '=', 'done')] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            res[product_id]['incoming'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['outgoing'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
        return res

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
    grouped = fields.Boolean('Agrupar por meses compras y ventas')

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
    scale = fields.Selection ([('25', '25%'),
                               ('50', '50%'),
                               ('60', '60%'),
                               ('75', '75%'),
                               ('100', '100%')], string="Scale")

    product_template_ids = fields.Many2many('product.template', string="Lista de plantillas")


    def get_grouped_moves(self, variant, company= False, done_qty = True):

        if done_qty:
            s_qty = 'product_uom_qty'
            p_qty = 'product_qty'
        else:
            s_qty = 'qty_delivered'
            p_qty = 'qty_received'

        where = " and sol.product_id = {}".format(variant.id)
        if self.date_start:
            where = ' and {} and so.order_date >= {}'.format(where, self.date_start)
        if self.date_end:
            where = ' and {} and so.order_date < {}'.format(where, self.date_end)
        if company:
            where = ' and {} and so.company_id = {}'.format(where, company )
        sql = "select extract(month from so.date_order) as month, sum(sol.{}) from sale_order_line sol join sale_order so on so.id = sol.order_id where so.state in ('sale', 'done') {} " \
              "group by extract(month from so.date_order), product_id".format(s_qty, where)

        self._cr.execute(sql)
        sale_lines = self._cr.fetchall()

        where = " and pol.product_id = {}".format(variant.id)
        if self.date_start:
            where = ' and {} and po.order_date >= {}'.format(where, self.date_start)
        if self.date_end:
            where = ' and {} and po.order_date < {}'.format(where, self.date_end)
        if company:
            where = ' and {} and po.company_id = {}'.format(where, company)
        sql = "select extract(month from po.date_order) as month, sum(pol.{}) from purchase_order_line pol join purchase_order po on po.id = pol.order_id where po.state in ('purchase', 'done') {} " \
              "group by extract(month from po.date_order), product_id".format(p_qty, where)

        self._cr.execute(sql)
        purchase_lines = self._cr.fetchall()
        months =[]
        for row in purchase_lines:
            months.append(row[0])
        for row in sale_lines:
            months.append(row[0])


        months = list(set(months))
        print("Meses: {}".format(months))
        return sale_lines, purchase_lines, months

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
        domain = []
        if self.scheduled_id:
            domain += [('scheduled_sale_id', '=', self.scheduled_id.id)]
        if self.brand_id:
            domain += [('product_brand_id', '=', self.brand_id.id)]
        if self.categ_id:
            domain += [('categ_id', 'child_of', self.categ_id.id)]
        if self.product_template_ids:
            domain += [('id', '=', self.product_template_ids.ids)]
        if self.pricelist_id:
            global_domain = [('pricelist_id', '=', self.pricelist_id.id), ('applied_on', '=', '3_global')]
            global_price_template_ids = self.env['product.pricelist.item'].search(global_domain)
            if not global_price_template_ids:

                template_domain = [('pricelist_id', '=', self.pricelist_id.id), ('applied_on', '=', '1_product')]
                price_template_ids = self.env['product.pricelist.item'].search(template_domain).mapped('product_tmpl_id')

                product_domain = [('pricelist_id', '=', self.pricelist_id.id), ('applied_on', '=', '0_product_variant')]
                price_product_ids = self.env['product.pricelist.item'].search(product_domain).mapped('product_id').mapped('product_tmpl_id')

                domain += [('id', 'in', price_template_ids.ids + price_product_ids.ids)]
        print (domain)
        templates = self.env['product.template'].search(domain, limit=self.limit)
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
        stock_info_moves = all_variants._compute_move_quantities_dict(
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
                'grouped_sale': [],
                'grouped_purchase': [],
                'grouped_months': []

            }
            sales=purchases=incomings=outgoings=stocks=0
            for variant in tmp.product_variant_ids:
                attr_name = ''
                if variant.attribute_value_ids:
                    attr_name = variant.attribute_value_ids[0].name
                res[tmp.name]['attr_names'].append(attr_name)
                if self.catalog_type_id.grouped:
                    res[tmp.name]['grouped_sale'], res[tmp.name]['grouped_purchase'], res[tmp.name]['grouped_months'] = self.get_grouped_moves(variant)

                if self.catalog_type_id.sales:
                    sales = self.get_variant_sales(variant)
                    res[tmp.name]['sales'].append(sales)

                if self.catalog_type_id.purchases:
                    purchases = self.get_variant_purchases(variant)
                    res[tmp.name]['purchases'].append(purchases)

                if self.catalog_type_id.incomings:
                    incomings = stock_info_moves[variant.id]['incoming']
                    res[tmp.name]['incomings'].append(incomings)

                if self.catalog_type_id.outgoings:
                    outgoings = stock_info_moves[variant.id]['outgoing']
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
