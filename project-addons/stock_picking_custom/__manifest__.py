# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Stock Picking Custom Anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'stock'
        #'stock_batch_picking',

        #'sale_order_line_tree'
    ],
    'data': [
        #'views/stock_batch_picking.xml',
        'views/stock_location.xml',

        #'wizard/sale_manage_variant_view.xml'
    ],
    'installable': True,
}
