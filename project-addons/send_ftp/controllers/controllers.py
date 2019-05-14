# -*- coding: utf-8 -*-
from odoo import http

# class SendFtp(http.Controller):
#     @http.route('/send_ftp/send_ftp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/send_ftp/send_ftp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('send_ftp.listing', {
#             'root': '/send_ftp/send_ftp',
#             'objects': http.request.env['send_ftp.send_ftp'].search([]),
#         })

#     @http.route('/send_ftp/send_ftp/objects/<model("send_ftp.send_ftp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('send_ftp.object', {
#             'object': obj
#         })