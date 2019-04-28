# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Product Custom Anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'product_tags',
        'base',
        'account',
        'sale',
        'stock_available_global',
        'product_virtual_stock_conservative',
        'stock_available_global',
        'partner_custom_anz',
    ],
    'data': [
        'views/partner_view.xml',
        'views/product_view.xml',
        'views/product_pricelist_view.xml',
        'views/operating_unit.xml',
        'views/product_tag.xml',
        'wizard/product_import_wzd_view.xml',
        'wizard/product_check_barcodes_view.xml',
        'security/ir.model.access.csv',
        'security/custom_product_rules.xml',
    ],
    'installable': True,
}
