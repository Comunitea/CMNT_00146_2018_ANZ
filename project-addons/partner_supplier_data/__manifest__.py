# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Supplier partner data',
    'version': '11.0.0.0.0',
    'category': 'Partner',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'base',
    ],
    'data': [
        'views/partner_view.xml',
        'views/partner_supplier_data.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
