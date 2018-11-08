# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Partner Area',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'product_brand',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/res_partner_area.xml',
        'views/product_brand.xml',
    ],
    'installable': True,
}
