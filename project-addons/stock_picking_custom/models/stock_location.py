# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'

    @api.multi
    def set_barcode_field(self):
        for location in self:
            if location.posx or location.posy or location.posz:

                barcode = "{:02d}.{:02d}.{:02d}".format(location.posx, location.posy, location.posz)
                if location.location_id:
                    barcode_location = "{:05d}".format(location.location_id.id)
                    location.barcode = "{}.{}".format(barcode_location, barcode)
                else:
                    location.barcode = "{:05d}".format(location.id)

