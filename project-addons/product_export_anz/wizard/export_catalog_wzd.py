
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _, api
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from pprint import pprint
import logging
from io import BytesIO
from base64 import b64encode
_logger = logging.getLogger(__name__)


try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')

class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _compute_move_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False, filter_state= 'all'):

        #return self._compute_quantities_dict(lot_id, owner_id, package_id, from_date=from_date, to_date=to_date)
        if filter_state == 'all':
            filter_state= [('state', 'not in', ('cancel', 'draft'))]
        elif filter_state == 'done':
            filter_state = [('state', '=', 'done')]
        else:
            filter_state = [('state', 'not in', ('done', 'cancel', 'draft'))]

        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if from_date:
            domain_move_in += [('date', '>=', from_date)]
            domain_move_out += [('date', '>=', from_date)]
        if to_date:
            domain_move_in += [('date', '<=', to_date)]
            domain_move_out += [('date', '<=', to_date)]

        Move = self.env['stock.move']
        domain_move_in_todo = filter_state + domain_move_in
        domain_move_out_todo = filter_state + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            res[product_id] = {}
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
            # if moves_in_res[product_id]:
            #     res[product_id]['incoming'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
            # else:
            #     res[product_id]['incoming'] = []
            # if moves_out_res[product_id]:
            #     res[product_id]['outgoing'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
            # else:
            #     res[product_id]['outgoing'] = []
        return res


class ProductCategory(models.Model):
    _inherit = "product.category"

    sequence = fields.Integer('Sequence', default=1, help="The first in the sequence is the default one.")

class CatalogType(models.Model):
    _name = 'export.catalog.type'

    name = fields.Char('Name')
    incomings = fields.Boolean('Inputs')
    outgoings = fields.Boolean('Outputs')
    purchases = fields.Boolean('Purchases')
    sales = fields.Boolean('Sales')
    stocks = fields.Boolean('Stocks')
    pvp = fields.Boolean('PVP')
    cost = fields.Boolean('Cpst')
    company_header = fields.Char('Company header')
    image = fields.Boolean('Template Image')
    image_scale = fields.Integer('Escala de la imagen (en %)', default=100)
    x_offset = fields.Integer('Posición de la imagen', default=80)
    image_field = fields.Selection([('image', 'Grande'), ('image_medium', 'Mediana'), ('image_small', 'Pequeña')])
    total = fields.Boolean('Total')
    euros = fields.Boolean('€')
    show_per_cent = fields.Boolean('% en resumen')
    grouped = fields.Boolean('Agrupar por meses compras y ventas')
    min_template_row = fields.Integer('Filas minima', default=6)
    filter_state = fields.Selection(
        [('all', 'Todos los movimientos'), ('done', 'Moviemintos realizados'), ('not_done', 'Moviemientos pendientes')],
        string="Filtro de movimientos",
        help="Filtra los movimientos según el estado. Permite visualizar entradas y salidas a futuro.")
    select_price = fields.Selection([('pvp', 'PVP'), ('venta', 'Previo de venta'), ('tarifa', 'Tarifa')],string="PVP/Precio de venta")

class ExportCatalogtWzd(models.TransientModel):

    _name = 'export.catalog.wzd'

    binary_field = fields.Binary("Descarga")
    binary_name = fields.Char("Descarga", compute="get_excel_name")
    scheduled_id = fields.Many2one('scheduled.sale', string='Scheduled')
    brand_id = fields.Many2one('product.brand', string='Brand')
    categ_id = fields.Many2one('product.category', string='Category')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    image_scale = fields.Integer('Escala de la imagen (en %)', default=100)
    x_offset = fields.Integer('Posición de la imagen', default=80)
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    with_stock = fields.Boolean("Solo con stock", help="Si está marcado solo artículos con stock")
    catalog_type_id = fields.Many2one('export.catalog.type', 'Catalog type', required=True)
    limit = fields.Integer('Limit', default=50)
    scale = fields.Selection ([('25', '25%'),
                               ('50', '50%'),
                               ('60', '60%'),
                               ('75', '75%'),
                               ('100', '100%')], default='100', string="Tamaño del fichero generado")
    location_id = fields.Many2one('stock.location', 'Ubicación para consultar stock', default=12)
    product_template_ids = fields.Many2many('product.template', string="Lista de plantillas")
    filter_state = fields.Selection([('all', 'Todos los movimientos'), ('done', 'Moviemintos realizados'), ('not_done', 'Moviemientos pendientes')],
                                    string="Filtro de movimientos",
                                    help="Filtra los movimientos según el estado. Permite visualizar entradas y salidas a futuro.")

    @api.multi
    def get_excel_name(self):
        res = []
        for wzd in self:
            name = wzd.catalog_type_id.name or 'Catalogo %s '%wzd.id
            if wzd.brand_id:
                name = '%s. %s' % (name, wzd.brand_id.name)
            if wzd.scheduled_id:
                name = '%s. %s' % (name, wzd.scheduled_id.name)
            if wzd.pricelist_id:
                name = '%s. %s' % (name, wzd.pricelist_id.name)
            wzd.binary_name = '%s.xls'%name



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
        ctx = self._context.copy()
        if self.pricelist_id:
            ctx.update(pricelist=self.pricelist_id.id)

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
                domain += [('id', 'in', price_template_ids.ids + price_product_ids.ids + self.product_template_ids.ids)]

        if self.with_stock:

            templates = self.env['product.template'].search(domain)
            product_ids = templates.mapped('product_variant_ids').ids
            quant_domain = [('product_id', 'in', product_ids), ('location_id', 'child_of', self.location_id.id)]
            res = self.env['stock.quant'].read_group(quant_domain, ['quantity', 'product_id'], 'product_id')
            product_ids_with_stock = [x['product_id'][0] for x in res if x['quantity'] > 0]

            template_domain = [('id', 'in', product_ids_with_stock)]
            tmpl_ids = self.env['product.product'].search_read(template_domain, ['product_tmpl_id'])
            if tmpl_ids:
                domain = [('id', 'in', [x['product_tmpl_id'][0] for x in tmpl_ids])]
            else:
                domain = []
        if self.limit>0:
            templates = self.env['product.template'].with_context(ctx).search(domain, limit=self.limit)
        else:
            templates = self.env['product.template'].with_context(ctx).search(domain)

        #if self.with_stock:
        #    return templates.filtered(lambda x: x.qty_available > 0)

        return templates


    def get_ordered_obj(self, templates):

        return templates.sorted(lambda x: x.categ_id.sequence * 1000 + (x.pvp or x.list_price), reverse=True)


    def get_report_vals(self):
        res = {}

        templates = self.get_templates()
        if not templates:
            raise UserError(_('No templates founded to export'))

        domain = [
            ('product_tmpl_id', 'in', templates.ids)
        ]
        all_variants = templates.mapped("product_variant_ids")
        stock_info = all_variants._compute_quantities_dict(
            False, False, False,
            from_date=self.date_start, to_date=self.date_end)
        stock_info_moves = all_variants._compute_move_quantities_dict(
            False, False, False,
            from_date=self.date_start, to_date=self.date_end, filter_state = self.catalog_type_id.filter_state)

        idx = 0
        tot = len(templates)


        for tmp in self.get_ordered_obj(templates):

            if self.catalog_type_id.select_price == 'pvp':
                precio_venta = tmp.pvp
            elif self.catalog_type_id.select_price == 'venta':
                precio_venta = tmp.lst_price
            else:
                precio_venta = tmp.price



            idx += 1
            _logger.info("Export template %s / %s" % (str(idx), str(tot)))
            new_template = {
                #'image': tmp.image_medium or False,
                'tmp_id': tmp.id,
                'cost': tmp.standard_price or tmp.product_variant_ids and tmp.product_variant_ids[0].standard_price or 0.00,
                'lst_price': tmp.pvp or tmp.lst_price,
                'pvp': tmp.price,
                'precio_venta': precio_venta,
                'attr_names': [],
                'sales': [],
                'purchases': [],
                'incomings': [],
                'outgoings': [],
                'stocks': [],
                'percent': 0.00,
                'grouped_sale': [],
                'grouped_purchase': [],
                'grouped_months': [],
                'ref_template': tmp.ref_template
            }
            sales = purchases = incomings = outgoings = stocks = 0
            t_sales = t_purchases = t_incomings = t_outgoings = t_stocks = 0
            variants = tmp.product_variant_ids.sorted(
                lambda x: x.attribute_value_ids and
                x.attribute_value_ids.filtered('main').sequence or 0)

            # Si la plantilla no tiene variantes evitar el calculo
            #  sino el total_field = [], pisará el de la última iteración
            # y habrá fallo mas adelane al no meter en heder_vals lo que debe
            if not variants:
                continue

            if self.with_stock:
                variants = variants.filtered(lambda x: x.qty_available > 0)
            total_field = []
            for variant in variants:
                attr_name = ''
                if variant.attribute_value_ids:
                    attr_name = variant.attribute_value_ids.filtered('main').name
                new_template['attr_names'].append(attr_name)

                if self.catalog_type_id.grouped:
                    new_template['grouped_sale'], new_template['grouped_purchase'], new_template['grouped_months'] = self.get_grouped_moves(variant)

                if self.catalog_type_id.sales:
                    sales = self.get_variant_sales(variant)
                    new_template['sales'].append(sales)
                    t_sales = sales
                    total_field+=['sales']

                if self.catalog_type_id.purchases:
                    purchases = self.get_variant_purchases(variant)
                    new_template['purchases'].append(purchases)
                    t_purchases += purchases
                    total_field += ['purchases']


                if self.catalog_type_id.incomings:
                    incomings = stock_info_moves[variant.id]['incoming_qty']
                    new_template['incomings'].append(incomings)
                    t_incomings = incomings
                    total_field += ['incomings']

                if self.catalog_type_id.outgoings:
                    outgoings = stock_info_moves[variant.id]['outgoing_qty']
                    new_template['outgoings'].append(outgoings)
                    t_outgoings = outgoings
                    total_field += ['outgoings']

                if self.catalog_type_id.stocks:
                    stocks = stock_info[variant.id]['qty_available']
                    new_template['stocks'].append(stocks)
                    t_stocks += stocks
                    total_field += ['stocks']

                if self.catalog_type_id.show_per_cent:
                    if incomings and outgoings:
                        percent = round(incomings/outgoings * 100, 2)
                    elif purchases and sales:
                        percent = round(sales/purchases * 100, 2)
                    else:
                        percent = 0
                    new_template['percent'] = percent


                for f in total_field:
                    new_template['total_' + f] = sum(x for x in new_template[f])

                if 'purchases' in total_field and 'sales' in total_field:
                    new_template['ventas_percent'] = int(100*(new_template['total_sales']/ new_template['total_purchases']) if new_template.get('total_purchases') else 0.0)
                new_template['moves_percent'] = int(100*(new_template['total_outgoings']/ new_template['total_incomings']) if new_template.get('total_incomings') else 0.0)

            if not tmp.ref_template:
                raise UserError ("Error: La plantilla {} no tiene referencia interna".format(tmp.display_name))
            res[tmp.ref_template] = new_template

        header_values = {}

        for f in total_field:
            header_values.update({f: 0})
        for tmp in res:
            for f in total_field:
                header_values[f] += res[tmp]['total_' + f]
        return res, header_values


    def export_catalog_xls(self):

        obj = 'report.product_export_anz.export_catalog_xls.xlsx'
        report = self.env[obj]#._get_objs_for_report(docids, data)
        objs = self#._get_objs_for_report(docids, data)
        file_data = BytesIO()
        # file_data = "/opt/odoo/catalog_id_%s.xls"
        data = {'context': self._context, 'wzd_id': self.id}
        workbook = xlsxwriter.Workbook(file_data, report.get_workbook_options())
        report.generate_xlsx_report(workbook, data, objs)
        workbook.close()
        # return
        file_data.seek(0)
        self.binary_field = b64encode(file_data.read())
        action = self.env.ref('product_export_anz.action_export_catalog').read()[0]
        action['res_id'] = self.id
        return action
