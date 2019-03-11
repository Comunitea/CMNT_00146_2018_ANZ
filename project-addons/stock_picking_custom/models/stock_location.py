# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'

    ubic = fields.Integer('Ubicación', default=0, help="Optional ubication details, for information purpose only")

    @api.multi
    def set_barcode_field(self):
        total = len(self)
        inc = 0
        for location in self.filtered(lambda x: x.usage == 'internal' and x.location_id.ubic):
            barcode = "{:02d}.{:02d}.{:02d}.{:02d}".format(location.location_id.ubic, location.posx, location.posy, location.posz)
            location.barcode = barcode
            inc += 1
            print ('{} de {} >> {}: Codigo: {}'.format(inc, total, location.display_name, location.barcode))


