# -*- coding: utf-8 -*-
from odoo import http

# class ImportImages(http.Controller):
#     @http.route('/import_images/import_images/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_images/import_images/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_images.listing', {
#             'root': '/import_images/import_images',
#             'objects': http.request.env['import_images.import_images'].search([]),
#         })

#     @http.route('/import_images/import_images/objects/<model("import_images.import_images"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_images.object', {
#             'object': obj
#         })