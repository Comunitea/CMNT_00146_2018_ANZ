# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Partner Custom Anzamar',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
        'account_analytic_default',
        'contract',
        'product_brand',
        'partner_area',
        'partner_fax',
        'operating_unit'
    ],
    'data': [
        'views/partner_view.xml',
'views/res_company.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
