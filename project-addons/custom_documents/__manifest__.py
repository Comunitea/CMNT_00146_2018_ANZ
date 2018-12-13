# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Custom documents',
    'version': '11.0.1.0.0',
    'summary': 'Cambios en formato de papel\n margen superior: 33; margen inferior 10; espaciado cabecera: 28',
    'category': '',
    'author': 'comunitea',
    'website': 'www.comunitea.com',
    'license': 'AGPL-3',
    'depends': [
        'web',
        'sale',
        'operating_unit',
        'sale_order_type',
        'sale_order_type_operating_unit',
        'sale_order_line_tree',
        'account_invoice_line_template',
        'account_due_dates_str',
        'account_reinvoice',
        'report_intrastat',
        'cmnt_custom_documents'
    ],
    'data': [
        'views/report_templates.xml',
        'views/sale_order_template.xml',
        'views/sale_report.xml',
        'views/report_invoice.xml',
        'views/account_report.xml'
    ],
    'installable': True,
}
