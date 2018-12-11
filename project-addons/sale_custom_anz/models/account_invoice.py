# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    sponsored = fields.Boolean(
        'Sponsored',
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.commercial_partner_id.risk_exception:
            warning = {
                    'title': _("Risk exceded for %s") %
                    self.commercial_partner_id.name,
                    'message': _("Financial risk exceeded."),
            }
            if not res:
                res = {}
            res['warning'] = warning
        return res


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    ref_change = fields.Boolean('Reference change')
