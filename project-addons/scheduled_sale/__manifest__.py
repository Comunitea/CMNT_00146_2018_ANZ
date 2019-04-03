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
        'sale',
        'sale_order_line_tree',
        'sale_custom_anz',
        'stock_picking_imp'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/scheduled_sale.xml',
        'views/product_view.xml',
        'views/stock_picking.xml',
        'report/sale_order_template.xml',
        'wizards/unlink_schedule_product.xml',
        'wizards/sale_manage_variant_view.xml'
    ],
    'installable': True,
}

