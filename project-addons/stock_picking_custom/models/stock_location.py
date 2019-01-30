# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'

    ubic = fields.Integer('Ubicación', default=0, help="Optional ubication details, for information purpose only")

    @api.multi
    def set_barcode_field(self, inc=0):
        total = len(self)
        for location in self.filtered(lambda x: x.usage == 'internal'):
            inc += 1
            barcode = ''
            if location.ubic > 0:
                barcode = "{:02d}".format(location.ubic)
            elif location.posx>0 or location.posy>0 or location.posz>0:
                barcode = ".{:02d}.{:02d}.{:02d}".format(location.posx, location.posy, location.posz)
                location.name = "{:02d}.{:02d}.{:02d}".format(location.posx, location.posy, location.posz)
            loc = location.location_id
            while loc and loc.ubic == 0:
                loc = loc.location_id
            if loc:
                barcode = "{}{}".format(loc.barcode, barcode)
            print ('{} de {} >> {}: Codigo: {}'.format(inc, total, location.display_name, location.barcode))
            location.barcode = barcode


    @api.multi
    @api.onchange('ubic', 'posx', 'posy', 'posz', 'location_id')
    def onchange_for_barcode(self):
        return self.set_barcode_field()