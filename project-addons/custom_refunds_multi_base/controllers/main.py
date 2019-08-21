# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64
import io
from werkzeug.utils import redirect

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.addons.sale.controllers.portal import CustomerPortal
from pprint import pprint

class CustomerPortalRefunds(CustomerPortal):
    @http.route([
        '/refunds_form/<int:order>',
    ], type='http', auth='user', website=True)
    def refunds_contact_form(self, order=None, access_token=None, **post):

        # Check if website.refunds_contact is active
        website = request.website
        values = {
            'order': order
        }
        if website.refunds_contact and order:
            return request.render("custom_refunds_multi_base.multi_base_contact_us_content_template", values)
        else:
            return request.redirect("/my/orders")