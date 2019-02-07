# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account invoice custom anz',
    'version': '11.0.1.0.0',
    'summary': 'Custom Anzamar',
    'category': 'Account',
    'author': 'comunitea',
    'website': 'www.comunitea.com',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice.xml',
        'views/payment_term_rule.xml'
    ],
    'installable': True,
}
