# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request
from odoo.addons.payment_redsys.controllers.main import RedsysController

_logger = logging.getLogger(__name__)


class RedsysControllerCustom(RedsysController):

    @http.route([
        '/payment/redsys/return',
        '/payment/redsys/cancel',
        '/payment/redsys/error',
        '/payment/redsys/reject',
    ], type='http', auth='none', csrf=False)
    def redsys_return(self, **post):
        """ Redsys."""
        _logger.info('Redsys: entering form_feedback with post data %s',
                     pprint.pformat(post))
        if post:
            request.env['payment.transaction'].sudo().form_feedback(
                post, 'redsys')

        return werkzeug.utils.redirect("payment/redsys/result/redsys_result_ok")
