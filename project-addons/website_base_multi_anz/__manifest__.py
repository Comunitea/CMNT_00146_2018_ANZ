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
    'name': 'MultiWebsite Base Module Anzamar',
    'version': '1.0',
    'summary': 'BackEnd customization for all companies and their websites.',
    'description': '',
    'category': 'Website',
    'author': 'Comunitea',
    'website': 'http://www.comunitea.com',
    'license': 'AGPL-3',
    'contributors': [
        'Pavel Smirnov <pavel@comunitea.com>',
        'Rubén Seijas <ruben@comunitea.com>',
        'Juan Vázquez Moreno <vmjuan90@gmail.com>',
    ],
    'depends': [
        'ecommerce_base',
        'seo_base',
        'breadcrumbs_base',
        'website_blog_base',
        'follow_us_base',
        'multi_company_base',
        'website_multi_company_blog',
        'mass_mailing',
        'website_form_builder',
        'website_sale_product_brand',
        'payment_redsys',
        'website_sale_hide_price',
        'product_virtual_stock_conservative',
    ],
    'data': [
        'data/company_data.xml',
        # 'data/menu_data.xml',
        'data/page_data.xml',
        'data/website_data.xml',
        'templates/blog.xml',
        'templates/cart.xml',
        'templates/header.xml',
        'templates/snippets.xml',
        'templates/wishlist.xml',
        'views/product_attribute.xml',
        'views/res_company_views.xml',
        'views/website_views.xml',
        'views/public_category.xml',
        'views/product_template.xml',
        'views/res_config_settings_views.xml',
        'views/blog_blog.xml',
        'views/blog_post_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': [
        '/static/description/icon.png',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
