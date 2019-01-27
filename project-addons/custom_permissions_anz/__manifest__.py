# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Custom Permissions',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'sales_team',
        'sale',
        'product',
        'sale_order_type',
        'calendar',
        'delivery',
        'stock',
        'sale_commission',
        'commercial_rules',
        'sale_mrp'
    ],
    'data': [
        'security/custom_groups_rules.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/product_view.xml',
        'views/anz_salesman_menus.xml',
    ],
    'installable': True,
}
