# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Sale Order Custom Anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'operating_unit',
        'product_brand',
        'sale_order_type',
        'product_virtual_stock_conservative'
    ],
    'data': [
        'views/operating_unit.xml',
        'views/sale_order.xml'
    ],
    'installable': True,
}
