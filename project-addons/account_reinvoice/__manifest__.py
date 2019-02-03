# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Reinvoice',
    'summary': 'Lets create invoices to associates from supplier Invoices',
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
        'partner_paydays',
        'purchase',
        'product_brand',
        'sale_order_type',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/commission_security.xml',
        'views/account_invoice.xml',
        'views/purchase_order.xml',
        'views/product_brand.xml',
        'views/res_partner_view.xml',
        'views/reinvoice_rule.xml',
        'wizard/reinvoice_view.xml',
    ],
}
