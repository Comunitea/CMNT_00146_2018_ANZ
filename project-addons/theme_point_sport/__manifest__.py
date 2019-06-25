# -*- coding: utf-8 -*-
#
# © 2018 Comunitea
# Pavel Smirnov <pavel@comunitea.com>
# Rubén Seijas <ruben@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#
##############################################################################
#
#    Copyright (C) {year} {company} All Rights Reserved
#    ${developer} <{mail}>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Point sport Theme',
    'version': '1.0',
    'summary': 'FrontEnd customization for Point sport Website',
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
        # 'theme_anzamar',
        'breadcrumbs_base',
        # 'seo_base',
        'website_blog_base',
        # 'follow_us_base',
        'multi_company_base',
        'website_base_multi_anz',
        'website_sale_hide_price',
    ],
    'data': [
        'data/theme_data.xml',
        'data/website_data.xml',
        'data/legal_data.xml',
        'data/menu_data.xml',
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
        'templates/shop.xml',
        'templates/product.xml',
        'templates/account.xml',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
