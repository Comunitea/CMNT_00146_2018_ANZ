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
        sheet = workbook.add_worksheet('Hoja 1')
        # SIZE COLUMNS
        sheet.set_column('A:A', 40)
        sheet.set_column('B:C', 10)
        sheet.set_column('D:D', 10)
        sheet.set_column('E:Z', 20)

        # FORMAT DECLARATIONS
        f_header = workbook.add_format({
            'bold': True, 'bg_color': '#cccccc', 'border': True
        })
        f_border = workbook.add_format({'border': True})

        # REPORT HEADE LINES
        sheet.write(0, 0, 'A N Z A M A R        POSINT-SPORT')

        sheet.write(1, 0, 'ESTADISTICA POR MODELOS')
        sheet.write(1, 1, time.strftime('%Y'))

        sheet.write(2, 2, 'TALLAS', f_header)
        sheet.write(2, 3, 'UNID', f_header)
        sheet.write(2, 3, '', f_header)
        sheet.write(2, 4, '', f_header)

        if data.get('brand_name', False):
            sheet.write(3, 0, 'PROVEEDOR: ' + data['brand_name'])  # TODO
        sheet.write(3, 2, 'ENTRADAS', f_border)
        sheet.write(3, 3, '', f_border)
        sheet.write(3, 4, '', f_border)

        sheet.write(4, 2, 'VENTAS', f_border)
        sheet.write(4, 3, '', f_border)
        sheet.write(4, 4, '', f_border)

        sheet.write(5, 0, 'TIPO    : ACCESORIOS')  # TODO
        sheet.write(5, 2, 'STOCKS', f_border)
        sheet.write(5, 3, '', f_border)
        sheet.write(5, 4, '', f_border)

        # TEMPLATE BLOCKS
        row = 8
        report_vals = data['report_vals']
        for tmp_name in report_vals:
            tmp_dic = report_vals[tmp_name]
            sheet.write(row, 0, 'MODELO', f_header)
            sheet.write(row, 1, 'COSTE', f_header)
            sheet.write(row, 2, 'PVP', f_header)
            row += 1

            # First row Values
            sheet.write(row, 0, tmp_name)
            sheet.write(row, 1, tmp_dic['cost'])
            sheet.write(row, 2, tmp_dic['pvp'])
            pvp_cell = xl_rowcol_to_cell(row, 2)
            row += 1

            # ???
            # sheet.write(row, 0, 'MARZO, JUNIO, SEPT Y OCT')
            row += 1

            # Write template image
            if tmp_dic['image']:
                image_data = io.BytesIO(base64.b64decode(tmp_dic['image']))
                img_dic = {
                    'image_data': image_data,
                    'x_scale': 0.2,
                    'y_scale': 0.2,
                    'x_offset': 60}
                sheet.insert_image(row, 0, 'image_medium.png', img_dic)

            col = 3
            # Write attributes table
            sheet.write(row, col, 'TALLAS', f_header)
            sheet.write(row + 1, col, 'ENTRADAS', f_border)
            sheet.write(row + 2, col, 'VENTAS', f_border)
            sheet.write(row + 3, col, 'STOCKS', f_border)

            attr_names = tmp_dic['attr_names']
            attr_values = [
                tmp_dic['incomings'],
                tmp_dic['sales'],
                tmp_dic['stocks'],
            ]
            col = 4
            sum_col = 0
            for attr_name in attr_names:
                sheet.write(row, col + sum_col, attr_name, f_header)
                sum_col += 1
            sheet.write(row, col + sum_col, 'TOTAL', f_header)

            sum_row = 0
            sum_col = 0
            row += 1
            for value_list in attr_values:
                init = xl_rowcol_to_cell(row + sum_row, col + sum_col)
                for value in value_list:
                    sheet.write_number(row + sum_row, col + sum_col, value,
                                       f_border)
                    sum_col += 1
                end = xl_rowcol_to_cell(row + sum_row, col + sum_col - 1)

                # TOTAL
                form = '=SUM(' + init + ':' + end + ')'
                sheet.write_formula(
                    row + sum_row, col + sum_col, form, f_border)

                # TOTAL AMOUNT
                total_cell = xl_rowcol_to_cell(row + sum_row, col + sum_col)
                form2 = '=' + total_cell + '*' + pvp_cell
                money = workbook.add_format({'num_format': '#,##0.00€'})
                sheet.write_formula(
                    row + sum_row, col + sum_col + 1, form2, money)

                sum_row += 1
                sum_col = 0
            row += 7
