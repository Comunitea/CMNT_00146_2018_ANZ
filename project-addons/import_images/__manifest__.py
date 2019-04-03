# -*- coding: utf-8 -*-
{
    'name': "import_images",

    'summary': """
        import images from folder
        """,

    'description': """
        import images from folder
    """,

    'author': "Juan Vázquez Moreno",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/wizard_views.xml',
    ],

}
