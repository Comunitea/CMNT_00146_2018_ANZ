# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Scheduled sale anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/scheduled_sale.xml',
    ],
    'installable': True,
}
