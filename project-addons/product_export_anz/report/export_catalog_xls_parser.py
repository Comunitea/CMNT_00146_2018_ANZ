# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models
import base64
import io
import time
from xlsxwriter.utility import xl_rowcol_to_cell


class ExportCatalogXlsParser(models.AbstractModel):
    """
    Parser to get data of report export catalog all
    """
    _name = 'report.product_export_anz.export_catalog_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):

        row_margin = 2

        page_rows = 50
        wzd = self.env['export.catalog.wzd'].browse(data['wzd_id'])

        scheduled_id = wzd.scheduled_id
        brand_id = wzd.brand_id or scheduled_id and scheduled_id.product_brand_id or False
        categ_id = wzd.categ_id
        pricelist_id = wzd.pricelist_id or scheduled_id and scheduled_id.pricelist_id or False
        scheduled_id = wzd.scheduled_id
        catalog_id = wzd.catalog_type_id

        sheet = workbook.add_worksheet('Hoja 1')
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.set_print_scale(int(wzd.scale))
        # SIZE COLUMNS
        sheet.set_column('A:A', 30)
        sheet.set_column('B:C', 10)
        sheet.set_column('D:D', 10)
        sheet.set_column('E:Z', 10)

        # FORMAT DECLARATIONS
        f_header = workbook.add_format({
            'bold': True,
            'bg_color': '#cccccc',
            'border': True
        })
        f_header2 = workbook.add_format({
            'bg_color': '#eeeeee',
            'border': True
        })
        f_border = workbook.add_format({'border': True})
        money = workbook.add_format({'num_format': '#,##0.00€'})
        title = workbook.add_format({'font_size': 14,
                                     'bold': True,
                                     'font_color': 'cyan',
                                     'bg_color': 'navy'})


        money_with_border = workbook.add_format({'border': True, 'num_format': '#,##0.00€'})
        percent_with_border = workbook.add_format({'border': True, 'num_format': '#,##0.00%'})
        # REPORT HEADE LINES
        if catalog_id.company_header:
            sheet.write(0, 0, catalog_id.company_header, title)

        sheet.write(1, 0, catalog_id.name, title)
        sheet.write(1, 1, time.strftime('%Y'))

        initial_row = 3
        row_info = initial_row

        if wzd.date_start:
             sheet.write(row_info, 0, 'Desde', f_header)
             sheet.write(row_info, 1, wzd.date_start)
             row_info +=1   
        if wzd.date_end:
             sheet.write(row_info, 0, 'hasta', f_header)
             sheet.write(row_info, 1, wzd.date_end)
             row_info += 1
        if brand_id:
            sheet.write(row_info, 0, 'PROVEEDOR: ', f_header)
            sheet.write(row_info, 1, brand_id.name)
            row_info += 1
        if scheduled_id:
            sheet.write(row_info, 0, 'PROGRAMACIÓN: ', f_header)
            sheet.write(row_info, 1, scheduled_id.name)
            row_info += 1
        if pricelist_id and catalog_id.euros:
            sheet.write(row_info, 0, 'LISTA DE PRECIOS: ', f_header)
            sheet.write(row_info, 1, pricelist_id.name)
            row_info +=1
        if categ_id:
            sheet.write(row_info, 0, 'CATEGORÍA:', f_header)
            sheet.write(row_info, 1, categ_id.name)
            row_info +=1
        
        
        row_header  = initial_row

        col = 3
        resumen_initial_col = col +1
        resumen_initial_row = row_header + 1
        sheet.write(row_header, col + 1, 'TALLAS', f_header2)
        if catalog_id.total:
            sheet.write(row_header, col + 2, 'TOTAL', f_header2)
        if catalog_id.euros:
            sheet.write(row_header, col + 3, '€', f_header)
        #sheet.write(row_header, col + 4, '', f_header)
        row_header += 1

        if catalog_id.purchases:
            sheet.write(row_header, col + 1, 'COMPRAS', f_header2)
            sheet.write(row_header, col + 2, '', f_border)
            sheet.write(row_header, col + 3, '', f_border)
            row_header +=1

        if catalog_id.incomings:
            sheet.write(row_header, col + 1, 'ENTRADAS', f_header2)
            sheet.write(row_header, col + 2, '', f_border)
            sheet.write(row_header, col + 3, '', f_border)
            row_header+=1

        if catalog_id.sales:
            sheet.write(row_header, col + 1, 'VENTAS', f_header2)
            sheet.write(row_header, col + 2, '', f_border)
            sheet.write(row_header, col + 3, '', f_border)
            row_header += 1

        if catalog_id.outgoings:
            sheet.write(row_header, col + 1, 'SALIDAS', f_header2)
            sheet.write(row_header, col + 2, '', f_border)
            sheet.write(row_header, col + 3, '', f_border)
            row_header += 1

        if catalog_id.stocks:
            sheet.write(row_header, col + 1, 'STOCKS', f_header2)
            sheet.write(row_header, col + 2, '', f_border)
            sheet.write(row_header, col + 3, '', f_border)


        # TEMPLATE BLOCKS
        row = initial_row + max(row_header, row_info) + row_margin
        report_vals = wzd.get_report_vals()
        page_breakers = []
        page_row = row
        template_len = 0
        for tmp_name in report_vals:

            tmp_dic = report_vals[tmp_name]
            sheet.write(row, 0, 'MODELO', f_header)
            sheet.write(row+1, 0, tmp_name)
            cols = 1
            if catalog_id.cost:
                sheet.write(row, cols, 'COSTE', f_header)
                sheet.write(row + 1, 1, tmp_dic['cost'])
                cols+=1
            if catalog_id.pvp:
                sheet.write(row, cols, 'PVP', f_header)
                sheet.write(row + 1, 2, tmp_dic['pvp'])
            row += 1

            # First row Values
            pvp_cell = xl_rowcol_to_cell(row, 2)
            row += 2


            # Write template image
            tmp_obj = self.env['product.template'].browse(tmp_dic['tmp_id'])
            if catalog_id.image and tmp_obj.image_medium:
                image_data = io.BytesIO(base64.b64decode(tmp_obj.image_medium))
                img_dic = {
                    'image_data': image_data,
                    'x_scale': 0.2,
                    'y_scale': 0.2,
                    'x_offset': 60}
                sheet.insert_image(row, 0, 'image_medium.png', img_dic)


            col = 3
            # Write attributes table
            sheet.write(row, col, 'TALLAS', f_header)
            tmpl_row = row
            attr_names = tmp_dic['attr_names']
            attr_values = []


            if catalog_id.purchases:
                tmpl_row +=1
                purchases_row = tmpl_row
                sheet.write(purchases_row, col, 'PURCHASES', f_border)
                attr_values += [tmp_dic['purchases']]

            if catalog_id.incomings:
                tmpl_row +=1
                incomings_row = tmpl_row
                sheet.write(incomings_row, col, 'ENTRADAS', f_border)
                attr_values += [tmp_dic['incomings']]

            if catalog_id.sales:
                tmpl_row +=1
                sales_row = tmpl_row
                sheet.write(sales_row, col, 'VENTAS', f_border)
                attr_values += [tmp_dic['sales']]

            if catalog_id.outgoings:
                tmpl_row +=1
                outgoings_row = tmpl_row
                sheet.write(outgoings_row, col, 'SALIDAS', f_border)
                attr_values += [tmp_dic['outgoings']]

            if catalog_id.stocks:
                tmpl_row +=1
                stocks_row = tmpl_row
                sheet.write(stocks_row, col, 'STOCKS', f_border)
                attr_values += [tmp_dic['stocks']]





            col = 4
            sum_col = 0
            #MARCO LAS TALLAS
            for attr_name in attr_names:
                sheet.write(row, col + sum_col, attr_name, f_header)
                sum_col += 1


            if catalog_id.total:
                sheet.write(row, col + sum_col, 'TOTAL', f_header)
                if catalog_id.euros:
                    sum_col += 1
                    sheet.write(row, col + sum_col, '€', f_header)
                if catalog_id.show_per_cent and catalog_id.incomings and catalog_id.outgoings:
                    sum_col += 1
                    sheet.write(row, col + sum_col, '%', f_header)
            sum_row = 0
            sum_col = 0
            row += 1

            #RECORRO verticalmente los valores para cada valoor importado
            for value_list in attr_values:
                row_val = row + sum_row
                init = xl_rowcol_to_cell(row_val, col + sum_col)
                # RECORRO horizontalmente los valores y los asignao a las tallas
                for value in value_list:
                    sheet.write_number(row_val, col + sum_col, value, f_border)
                    sum_col += 1

                end = xl_rowcol_to_cell(row_val, col + sum_col - 1)
                # TOTAL
                if catalog_id.total:
                    total_col = col + sum_col
                    form = '=SUM(' + init + ':' + end + ')'
                    sheet.write_formula(row_val, total_col, form, f_border)
                    total_cell = xl_rowcol_to_cell(row_val, total_col)
                    total_in = catalog_id.incomings and xl_rowcol_to_cell(incomings_row, total_col)
                    total_out = catalog_id.outgoings and xl_rowcol_to_cell(outgoings_row, total_col)

                    # TOTAL AMOUNT
                    if catalog_id.euros:
                        form_euros = '=' + total_cell + '*' + pvp_cell
                        total_col += 1
                        sheet.write_formula(row_val, total_col, form_euros, money_with_border)

                sum_row += 1
                sum_col = 0
                    # total %

            if catalog_id.show_per_cent and catalog_id.incomings and catalog_id.outgoings:
                form_per_cent = '={}/{}'.format(total_out, total_in)
                sheet.write_formula(row + sum_row - 1 , total_col + 1, form_per_cent, f_border)
                sum_row += 1



            row += sum_row + row_margin
            if not template_len:
                template_len = row - page_row
            if template_len:
                page_row += template_len
                if page_row + template_len > page_rows:
                    page_row = 1
                    page_breakers.append(row -1)


        #sheet.fit_to_pages(1, 0)
        sheet.set_h_pagebreaks(page_breakers)
        sheet.set_v_pagebreaks([25])
        print (page_breakers)
