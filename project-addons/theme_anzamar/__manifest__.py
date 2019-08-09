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
    'name': 'Anzamar Theme',
    'version': '1.0',
    'summary': 'FrontEnd customization for Anzamar Website',
    'description': '',
    'category': 'Website',
    'author': 'Comunitea',
    'website': 'http://www.comunitea.com',
    'license': 'AGPL-3',
    'contributors': [
        'Pavel Smirnov <pavel@comunitea.com>',
        'Rubén Seijas <ruben@comunitea.com>',
    ],
    'depends': [
        # 'breadcrumbs_base',
        # 'website_blog_base',
        # 'follow_us_base',
        # 'multi_company_base',
        'website_base_multi_anz',
    ],
    'data': [
        'data/theme_data.xml',
        'data/website_data.xml',
        'data/menu_data.xml',
        'data/page_data.xml',
        'templates/snippets.xml',
        'templates/head.xml',
        'templates/header.xml',
        'templates/footer.xml',
        'templates/forms.xml',
        'templates/breadcrumbs_bar.xml',
        'templates/account.xml',
        'templates/newsletter.xml',
        'templates/pages.xml',
        'templates/page_home.xml',
        'templates/page_anzamar_group.xml',
        'templates/page_brand_black_laces.xml',
        'templates/page_brand_feel_point.xml',
        'templates/page_brand_goalkers.xml',
        'templates/page_brand_point_sport.xml',
        'templates/page_brand_skipping.xml',
        'templates/page_brand_umbro.xml',
        'templates/page_open_shop.xml',
        'templates/page_work_with_us.xml',
        'templates/shop.xml',
        'templates/product.xml',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
