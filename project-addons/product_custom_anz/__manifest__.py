# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Product Custom Anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'product_virtual_stock_conservative',
        'partner_custom_anz',
        'account',
        'sale'

    ],
    'data': [
        'views/partner_view.xml',
        'views/product_view.xml',
        'views/product_pricelist_view.xml',
        'views/operating_unit.xml',
        'wizard/product_import_wzd_view.xml',
    ],
    'installable': True,
}
