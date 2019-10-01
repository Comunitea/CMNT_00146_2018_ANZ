# -*- coding: utf-8 -*-
{
    'name': 'Point Sport Multi Theme',
    'version': '2.0',
    'summary': 'Frontend customization for Point sport Website',
    'description': '',
    'category': 'Theme',
    'author': 'Comunitea',
    'website': 'http://www.comunitea.com',
    'license': 'AGPL-3',
    'contributors': [
        'Pavel Smirnov <pavel@comunitea.com>',
        'Rubén Seijas <ruben@comunitea.com>',
    ],
    'depends': [
        'website_base_multi_anz',
    ],
    'data': [
        'data/theme_data.xml',
        'data/website_data.xml',
        'data/menu_data.xml',
        'data/legal_data.xml',
        'data/page_data.xml',
        'templates/head.xml',
        'templates/header.xml',
        'templates/footer.xml',
        'templates/forms.xml',
        'templates/breadcrumbs_bar.xml',
        'templates/pages.xml',
        'templates/page_home.xml',
        'templates/page_work_with_us.xml',
        'templates/page_about_us.xml',
        'templates/page_contact_us.xml',
        'templates/page_contact_us_thanks.xml',
        'templates/page_our_shops.xml',
        'templates/page_open_shop.xml',
        'templates/page_delivery_and_payment.xml',
        'templates/page_our_group.xml',
        'templates/shop.xml',
        'templates/product.xml',
        'templates/account.xml',
        'views/customize_views.xml',
    ],
    'images': [
        '/static/img/logo-horizontal.png',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
