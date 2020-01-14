# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Sale Order Custom Anzamar',
    'version': '11.0.2.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'product_custom_anz',
        'sale_order_line_date',
        'sale_order_type',
        'sale_order_variant_mgmt',
        'sale_stock'
        #'sale_order_line_tree'
    ],
    'data': [
        'data/ir_sequence.xml',
        'views/sale_order.xml',
        'views/account_invoice.xml',
        'views/product_product.xml',
        'views/pricelist.xml',
        'wizard/sale_manage_variant_view.xml',
        'report/sale_report_views.xml',
        'report/account_invoice_report_views.xml',
    ],
    'installable': True,
    'post_init_hook': 'set_product_ref_change_code',
}

