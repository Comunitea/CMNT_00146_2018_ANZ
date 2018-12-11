# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Sale Order Line Tree',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'partner_custom_anz',
        'product_custom_anz',
        'sale_order_variant_mgmt',
    ],
    'data': [
        'views/sale_order_tree.xml',
        'views/sale_order_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
