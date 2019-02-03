# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Custom commission anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'product_brand',
        'sale_commission'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/agent_commission_brand_view.xml',
        'views/partner_view.xml',
        'views/product_brand_view.xml',
        'views/report_settlement_grouped_template.xml'
    ],
    'installable': True,
}
