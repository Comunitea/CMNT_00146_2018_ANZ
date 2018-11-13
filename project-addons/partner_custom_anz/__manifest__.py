# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Partner Custom Anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'account_analytic_default',
        'contract',
        'product_brand',
        'partner_area',
        'product_custom_anz',
        'partner_fax',
        'operating_unit'
    ],
    'data': [
        'views/partner_view.xml',
        'views/account_invoice.xml'
    ],
    'installable': True,
}
