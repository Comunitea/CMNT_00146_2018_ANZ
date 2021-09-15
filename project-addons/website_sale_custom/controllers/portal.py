# -*- coding: utf-8 -*-
# © 2021 Comunitea - Vicente Ángel Gutiérrez <vicente@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import http
from odoo.http import request


class WebsitePayment(http.Controller):
    @http.route(['/shop/payment/confirm_order'], type='http', auth='public', website=True, sitemap=False)
    def confirm_all(self, **kw):
        sale_order_id = int(kw.get('sale_order_id', 0)) or request.website.sale_get_order()
        if sale_order_id:
            sale_order_id.with_context(send_email=False).action_confirm()
            tx = request.website.sale_get_transaction()
            if tx:
                if tx.state in ['done', 'authorized']:
                    status = 'success'
                    message = tx.acquirer_id.done_msg
                elif tx.state == 'pending':
                    status = 'warning'
                    message = tx.acquirer_id.pending_msg
                else:
                    status = 'danger'
                    message = tx.acquirer_id.error_msg
                return request.render('payment.confirm', {'tx': tx, 'status': status, 'message': message})
            return request.redirect('/shop/confirmation')
        else:
            return request.redirect('/my/home')
