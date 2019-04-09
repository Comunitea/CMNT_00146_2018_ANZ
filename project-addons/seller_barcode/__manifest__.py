# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Seller Barcodes',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base', 'website_sale', 'product_custom_anz'

    ],
    'data': [
        'security/ir.model.access.csv',
        'views/seller_barcode.xml',
        'views/product_tag.xml',

        'wizard/barcode_import_wzd_view.xml'
    ],
    'installable': True,
}
