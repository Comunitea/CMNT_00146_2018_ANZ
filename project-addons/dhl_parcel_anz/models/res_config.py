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

from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError
from ast import literal_eval

DHL_PARAMS = ['dhl_client_number_b2b', 'dhl_client_number_b2c']

class ConfigDHLData(models.TransientModel):

    _inherit = 'res.config.settings'

    dhl_client_number_b2b = fields.Char(string='DHL client number B2B', size=6)
    dhl_client_number_b2c = fields.Char(string='DHL client number B2C', size=6)

    @api.model
    def get_values(self):
        ICP =self.env['ir.config_parameter'].sudo()
        res = super(ConfigDHLData, self).get_values()
        for param in DHL_PARAMS:
            value= ICP.get_param('dhl_parcel_anz.{}'.format(param), False)
            res.update({param: value})
        return res

    @api.multi
    def set_values(self):
        super(ConfigDHLData, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        for param in DHL_PARAMS:
            ICP.set_param('dhl_parcel_anz.{}'.format(param), self[param])