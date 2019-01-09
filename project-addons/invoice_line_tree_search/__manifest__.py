# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Invoice Line Tree View Search',
    'summary': 'Invoice line tree search',
    'version': '11.0.1.0.0',
    'category': 'Custom',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [

        'account',

    ],
    'data': [

        'views/account_invoice_line.xml',
        'views/product_view.xml'

    ],
}
