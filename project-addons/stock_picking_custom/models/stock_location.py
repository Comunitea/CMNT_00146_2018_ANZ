# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'

    @api.multi
    def set_barcode_field(self):
        for location in self:
            barcode = ''
            if location.posx or location.posy or location.posz:
                barcode = "{:02d}.{:02d}.{:02d}".format(location.posx, location.posy, location.posz)
                location.name = "{:02d}-{:02d}-{:02d}".format(location.posx, location.posy, location.posz)
            loc = location.location_id
            while loc:
                if loc.barcode:
                    barcode = "{}.{}".format(loc.barcode, barcode)
                loc = loc.location_id
            print (barcode)
            location.barcode = barcode




