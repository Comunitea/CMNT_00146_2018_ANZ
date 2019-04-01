# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError

class StockLocation(models.Model):

    _inherit = 'stock.location'

    ubic = fields.Integer('Ubicación', default=0, help="Optional ubication details, for information purpose only")

    @api.multi
    def set_barcode_field(self):
        total = len(self)
        inc = 0
        print (self)
        for location in self:
            ubic = location.location_id and (location.location_id.ubic or location.location_id.id) or 0
            barcode = "{:05d}.{:02d}.{:02d}.{:02d}".format(ubic, location.posx, location.posy, location.posz)
            location.barcode = barcode
            inc += 1
            print ('{} de {} >> {}: Codigo: {}'.format(inc, total, location.display_name, location.barcode))

    @api.onchange('posx', 'posy', 'posz')
    def onchange_act_barcode(self):
        self.set_barcode_field()

    def check_vals(self, usage, posx, posy, posz, barcode):
        if usage=='internal' and not posx and not posy and not posz:
            raise ValidationError('Las ubicaciones internas  los campos cliente, tarifa, compañia y tipo de venta')
        if usage=='internal' and not barcode:
            raise ValidationError('Las ubicaciones internas deben tener un código de barras')

    @api.model
    def create(self, vals):
        self.check_vals(vals['usage'], vals['posx'], vals['posy'], vals['posz'], vals['barcode'])
        return super().create(vals)

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if len(self) == 1:
            self.check_vals(self.usage, self.posx, self.posy, self.posy, self.barcode)
        if 'ubic' in vals:
            for loc in self:
                locs = self.env['stock.location'].search([('usage','=', 'internal'), ('location_id', '=', loc.id)])
                locs.set_barcode_field()
        return res
