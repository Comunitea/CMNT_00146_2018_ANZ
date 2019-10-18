# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Stock Company Availability',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'stock',
        'stock_available_global'
    ],
    'data': [
        'views/stock_picking.xml',
        'views/stock_move.xml',
        'views/stock_location_path.xml',
        'views/stock_location.xml',
        'views/stock_picking_type.xml',
    ],
    'installable': True,
}
