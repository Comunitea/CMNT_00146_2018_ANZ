# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'


    @api.multi
    def set_barcode_field(self):
        for location in self:
            barcode = "{:02d}.{:02d}.{:02d}".format(location.posx, location.posy, location.posz)
            if barcode == '00.00.00':
                barcode = "{:04d}.000".format(location.id)
            location.barcode = "{}.{}".format("{:04d}".format(location.location_id.id), barcode)

    @api.multi
    def write(self, vals):
        res = super(StockLocation, self).write(vals)
        self.set_barcode_field()
        return res