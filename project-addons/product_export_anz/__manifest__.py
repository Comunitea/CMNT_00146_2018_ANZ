# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Product Export Anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'product_brand',
        'scheduled_sale',
        'report_xlsx',
    ],
    'data': [
        'views/report_view.xml',
        'views/product_view.xml',
        'security/ir.model.access.csv',
        'wizard/export_catalog_wzd_view.xml',
    ],
    'installable': True,
}
