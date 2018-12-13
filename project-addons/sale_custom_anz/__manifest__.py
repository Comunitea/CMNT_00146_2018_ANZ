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
        'product_custom_anz',
        'sale_order_line_date',
        'sale_order_type',
        'sale_order_variant_mgmt',
        'sale_order_line_tree'
    ],
    'data': [
        'views/sale_order.xml',
        'views/account_invoice.xml',
        'wizard/sale_manage_variant_view.xml'
    ],
    'installable': True,
}
