# -*- coding: utf-8 -*-
{
    'name': "custom_documents_anz",

    'summary': """
        A futuro, añade unas pocas views
	""",

    'description': """
        POS.xml - Modify simplify invoice for POS
    """,

    'author': "Juan Vázquez Moreno",
    'website': "http://www.anzamar.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
	# add receipt
	'qweb': [
		'static/pos.xml',
	],
	
	'installable': True,
}
