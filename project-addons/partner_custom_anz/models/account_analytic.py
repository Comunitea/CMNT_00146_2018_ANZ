# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class AccountAnalytic(models.Model):
    _inherit = "account.analytic.account"

    @api.model
    def create(self, vals):
        res = super(AccountAnalytic, self).create(vals)
        res.create_analytic_default()
        return res

    @api.multi
    def create_analytic_default(self):
        self.ensure_one()
        vals = {
            'analytic_id': self.id,
            'partner_id': self.partner_id.id
        }
        self.env['account.analytic.default'].create(vals)
