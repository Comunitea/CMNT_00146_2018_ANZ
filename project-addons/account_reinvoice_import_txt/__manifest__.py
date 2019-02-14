# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Invoice IMPORT TXT',
    'summary': 'Import txt from adidas, ...',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base',
        'account',
        'account_reinvoice',
        'account_invoice_check_total',
        'partner_paydays'

    ],
    'data': [
        'views/account_reinvoice_import_txt.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/account_invoice.xml'
    ],
}
