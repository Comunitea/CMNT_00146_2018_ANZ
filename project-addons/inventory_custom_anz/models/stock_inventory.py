# -*- coding: utf-8 -*-
# Copyright 2019 Kiko Sánchez, <kiko@comunitea.com> Comunitea Servicios Tecnológicos S.L.
# Copyright 2019 Vicente Gutiérrez, <vicente@comunitea.com> Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models, fields
from pprint import pprint
import logging

_logger = logging.getLogger(__name__)

class InventoryLine(models.Model):

    _inherit = "stock.inventory.line"

    def _get_quants(self):
        return self.env['stock.quant'].search([
            '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False),
            ('location_id', '=', self.location_id.id),
            ('lot_id', '=', self.prod_lot_id.id),
            ('product_id', '=', self.product_id.id),
            ('owner_id', '=', self.partner_id.id),
            ('package_id', '=', self.package_id.id)])

class StockInventory(models.Model):

    _inherit = "stock.inventory"

    def _get_inventory_lines_values(self):
        vals = super()._get_inventory_lines_values()
        # TDE CLEANME: is sql really necessary ? I don't think so
        locations = self.env['stock.location'].search([('id', 'child_of', [self.location_id.id])])
        domain = ' sq.location_id in %s AND pp.active'
        args1 = (tuple(locations.ids),)
        Product = self.env['product.product']
        # Empty recordset of products available in stock_quants
        quant_products = self.env['product.product']
        # Empty recordset of products to filter
        products_to_filter = self.env['product.product']

        # case 0: Filter on company
        if self.company_id:
            domain += ' AND sq.company_id is null '
            #args1 += (self.company_id.id,)

        #case 1: Filter on One owner only or One product for a specific owner
        if self.partner_id:
            domain += ' AND sq.owner_id = %s'
            args1 += (self.partner_id.id,)
        #case 2: Filter on One Lot/Serial Number
        if self.lot_id:
            domain += ' AND sq.lot_id = %s'
            args1 += (self.lot_id.id,)
        #case 3: Filter on One product
        if self.product_id:
            domain += ' AND sq.product_id = %s'
            args1 += (self.product_id.id,)
            products_to_filter |= self.product_id
        #case 4: Filter on A Pack
        if self.package_id:
            domain += ' AND sq.package_id = %s'
            args1 += (self.package_id.id,)
        #case 5: Filter on One product category + Exahausted Products
        if self.category_id:
            categ_products = Product.search([('categ_id', '=', self.category_id.id)])
            domain += ' AND sq.product_id = ANY (%s)'
            args1 += (categ_products.ids,)
            products_to_filter |= categ_products

        self.env.cr.execute("""SELECT sq.product_id as product_id, sum(quantity) as product_qty,
            sq.location_id as location_id, sq.lot_id as prod_lot_id, sq.package_id as package_id,
            sq.owner_id as partner_id
            FROM stock_quant sq
            LEFT JOIN product_product pp
            ON pp.id = sq.product_id
            WHERE %s
            GROUP BY sq.product_id, sq.location_id, sq.lot_id, sq.package_id, sq.owner_id """ % domain, args1)
        res_sql = self.env.cr.dictfetchall()
        cont = len(res_sql)

        for product_data in res_sql:
            _logger.info("%s. Inventory line para: %s"% (cont, product_data))
            cont -= 1
            # replace the None the dictionary by False, because falsy values are tested later on
            for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                product_data[void_field] = False
            product_data['theoretical_qty'] = product_data['product_qty']
            if product_data['product_id']:
                product_data['product_uom_id'] = Product.browse(product_data['product_id']).uom_id.id
                quant_products |= Product.browse(product_data['product_id'])
            vals.append(product_data)

        return vals