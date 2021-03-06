# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def create(self, vals):
        self2 = self.with_context(no_check_locations=True)
        return super(StockWarehouse, self2).create(vals)


class StockLocation(models.Model):

    _inherit = 'stock.location'
    _order = "sequence asc"

    ubic = fields.Integer('Secuencia de recorrido', default=0, help="Optional ubication details, for information purpose only")
    inverse_order = fields.Boolean(string='Inverse order', help="Mark for inverse order.")
    sequence = fields.Integer(string='Location order')

    @api.multi
    def set_barcode_field(self):
        total = len(self)
        inc = 0
        print (self)
        for location in self:
            ubic = location.location_id and (location.location_id.ubic or location.location_id.id) or 0
            barcode = "{:05d}{:02d}{:02d}{:02d}".format(ubic, location.posx, location.posy, location.posz)
            location.barcode = barcode
            inc += 1
            print ('{} de {} >> {}: Codigo: {}'.format(inc, total, location.display_name, location.barcode))

    @api.onchange('posx', 'posy', 'posz', 'location_id', 'location_id.ubic')
    def onchange_act_barcode(self):

        # self._set_order()
        self.set_barcode_field()

    def check_vals(self, usage, posx, posy, posz, barcode):
        if self._context.get('no_check_locations'):
            return True
        if usage=='internal' and not posx and not posy and not posz:
            raise ValidationError('Las ubicaciones internas  debenm tener valor en los campos  Pasillo (x), Estatntería (Y) Altura (Z)')
        if usage=='internal' and not barcode:
            raise ValidationError('Las ubicaciones internas deben tener un código de barras')
        return True

    @api.model
    def create(self, vals):
        self.check_vals(vals.get('usage'), vals.get('posx'), vals.get('posy'), vals.get('posz'), vals.get('barcode'))
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

    @api.multi
    def _set_order(self):
        count = len(self)
        index = 0
        for location in self.sudo():
            index += 1
            if location.location_id:
                ubic = location.location_id.ubic or location.location_id.id
                pasillo = location.posy if not location.location_id.inverse_order else (100-location.posy)
            else:
                ubic = location.id
                pasillo = location.posy
            sequence = "{:02d}{:02d}{:02d} ".format(location.location_id.ubic or location.posx, pasillo, location.posz)

            #ubic = location.location_id and (location.location_id.ubic or location.location_id.id) or 0
            barcode = "{:05d}{:02d}{:02d}{:02d}".format(ubic, location.posx, location.posy, location.posz)

            print('Ordenando {}/{}: Ubicación: {} Sec: {} y Codigo: {}'.format( index, count, location.name, sequence, barcode))
            location.update({
                'barcode': barcode,
                'sequence': int(sequence)
            })

    @api.multi
    def order_full_list(self):
        locations = self.env['stock.location'].search([])
        locations.filtered(lambda x: x.usage =='internal' and x.posx)._set_order()
