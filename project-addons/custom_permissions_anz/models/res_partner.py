# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """
        Only search customers withe the comercial equal to the user if
        group Salesman Anz checked.
        This funcionality is very difficult to reach with security rules.
        """
        anz_salesman_group = self.env.user.has_group(
            'custom_permissions_anz.anz_salesman')
        if anz_salesman_group:
            restrict_domain = [
                '|', ['user_id', '=', self._uid],
                ['commercial_partner_id', '=',  self._uid]
            ]
            args = (args or []) + restrict_domain
        return super(ResPartner, self).search(args, offset=offset,
                                              limit=limit, order=order,
                                              count=count)
