# -*- coding: utf-8 -*-
from odoo import http

# class CustomDocumentsAnz(http.Controller):
#     @http.route('/custom_documents_anz/custom_documents_anz/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_documents_anz/custom_documents_anz/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_documents_anz.listing', {
#             'root': '/custom_documents_anz/custom_documents_anz',
#             'objects': http.request.env['custom_documents_anz.custom_documents_anz'].search([]),
#         })

#     @http.route('/custom_documents_anz/custom_documents_anz/objects/<model("custom_documents_anz.custom_documents_anz"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_documents_anz.object', {
#             'object': obj
#         })