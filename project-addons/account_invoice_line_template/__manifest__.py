# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'account invoice line template',
    'version': '11.0.1.0.0',
    'summary': 'Group invoice lines by product template',
    'category': 'Account',
    'author': 'comunitea',
    'website': 'www.comunitea.com',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'sale_custom_anz'
    ],
    'data': [
        'views/account_invoice_line_template.xml',
        'views/account_invoice.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
