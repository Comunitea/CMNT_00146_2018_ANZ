# -*- coding: utf-8 -*-
##############################################################################
#    License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#    Copyright (C) 2019 Comunitea Servicios Tecnológicos S.L. All Rights Reserved
#    Vicente Ángel Gutiérrez <vicente@comunitea.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api, _, tools
from datetime import datetime, timedelta, time
from odoo.exceptions import ValidationError
import base64

class DHLFile(models.TransientModel):

    _name = 'dhl.txt.file'
    
    filename = fields.Char('File name', readonly=True)
    file_data = fields.Binary('File data', readonly=True)


class StockPickingDHL(models.Model):

    _inherit = 'stock.picking'

    number_of_packages = fields.Integer(string='Number of Packages', copy=False, default=1)

    @api.multi
    def create_dhl_file(self):
        now = datetime.now()
        filename = "DHL_PARCEL_{}.txt".format(now)
        f = open(filename,"w")
        if f:
            for picking in self:
                line = picking.create_dhl_line()
                f.write(line)
            f.close()
        else:
            raise ValidationError(_("There was a problem creating the file {}".format(filename)))
        
        try:
            file_ = open(filename,"r", encoding="utf8")
            data = file_.read()
            file_.close()
            dhl_file = self.env['dhl.txt.file'].create({
                'filename': filename,
                'file_data': base64.b64encode(str.encode(data))
            })
        except Exception as e:
            raise ValidationError(_('We could not create the DHL file because:\n%s.' % e))
        
        return {
            'name': _('Download File'),
            'res_id': dhl_file.id,
            'res_model': 'dhl.txt.file',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('dhl_parcel_anz.save_dhl_txt_file_done').id,
            'view_mode': 'form',
            'view_type': 'form',
        }

    def create_dhl_line(self):
        ICP =self.env['ir.config_parameter'].sudo()
        line = ''

        try:

            line += ICP.get_param('dhl_parcel_anz.dhl_client_number', False).zfill(6)
            line += '{:<1}'.format('')
            line += self.partner_id.country_id.code
            line += '{:<8}'.format('')
            line += '{:<2}'.format('')
            line += '{:<1}'.format('') # M (sea transport) or A (air transport) if the transport goes to Canarias/Tenerife/LasPalmas/Madeira/Azores Else empty.
            line += '{:<40}'.format(self.partner_id.name[:40] or self.partner_id.display_name[:40])
            line += '{:<40}'.format('{} {}'.format(self.partner_id.street or '', self.partner_id.street2 or '')[:40])
            line += '{:<20}'.format('{}, {}'.format(self.partner_id.city or '', self.partner_id.state_id.name or '')[:20])
            line += '{:<9}'.format(self.partner_id.zip or '')
            line += '{:<9}'.format((self.partner_id.mobile or self.partner_id.phone or '').replace('+34', '').replace(' ', ''))
            line += '{:<1}'.format('')
            line +=  '{:<35}'.format(self.name[:35])
            line += '{:<2}'.format('')
            line += "{}".format(self.number_of_packages).zfill(3)
            line += "{}".format(round(self.shipping_weight)).zfill(5)
            line += ''.zfill(5)
            line += ''.zfill(11)
            line += 'EUR'
            line += '{:<1}'.format('') # Money on arrival: (P) paid or (D) debt, else empty.
            line += ''.zfill(9) # Insurance amount.
            line += 'EUR'
            line += '{:<1}'.format('') # Insurance: (P) paid or (D) debt, else empty.
            line += '{:<1}'.format('') # Return signed note, (S) yes or empty.
            line += '{:<1}'.format('')
            line += '{:<40}'.format(self.delivery_note[:40] if self.delivery_note else "")
            line += '{:<40}'.format(self.delivery_note[40:] if self.delivery_note else "")
            line += '{:<1}'.format('') # Customs costs (P) paid or (D) else empty..
            line += '{:<8}'.format(datetime.strptime(self.scheduled_date, tools.DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d%m%Y'))
            line += '{:<125}'.format('')
            line += '{:<3}'.format('CPT') # Shipping: (CPT) Paid, (EXW) Debt. 
            line += '{:<3}'.format(800 if self.partner_id.country_id.code in ('ES', 'PT') else 110) #Spain/Portugal 800, else 110
            line += '{:<25}'.format('') # Must fill on International shipping
            line += '{:<70}'.format('') # Must fill on International shipping
            line += '{:<15}'.format('') # Must fill on International shipping
            line += '{:<3}'.format('') # Must fill on International shipping
            line += '{:<15}'.format('') # Optional on International shipping
            line += '{:<9}'.format('') # Must fill on International shipping
            line += '{:<10}'.format('') # Optional on International shipping
            line += 'ES'
            line += '{:<50}'.format(self.company_id.email)
            line += '{:<25}'.format('')
            line += '{:<50}'.format(self.partner_id.email)
            line += '{:<4}'.format('')
            line += '{:<90}'.format('')
        except Exception as e:
            raise ValidationError(_('We could not create the line for the stock picking %s because:\n%s.' % (self.name, e)))

        return line

