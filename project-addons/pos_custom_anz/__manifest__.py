# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Pos Custom Anz',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'point_of_sale',
        'commercial_rules_anz',
        'pos_order_return',
        'pos_order_mgmt',
        'pos_product_available',
        'pos_coupons_gift_voucher'
    ],
    'data': [
        'views/assets.xml',
        'views/pos_order_view.xml',
    ],
    'installable': True,
}
