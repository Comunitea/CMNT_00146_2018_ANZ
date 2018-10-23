# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    affiliate = fields.Boolean('Affiliate')
    player = fields.Boolean('Player')
    analytic_default_count = fields.Integer('Analytic Defaults',
                                            compute='_count_analytic_defaults')

    @api.multi
    def _count_analytic_defaults(self):
        for partner in self:
            domain = [('partner_id', '=', partner.id)]
            count = self.env['account.analytic.default'].search_count(domain)
            partner.analytic_default_count = count

    @api.multi
    def view_analytic_defaults(self):
        self.ensure_one()
        domain = [('partner_id', '=', self.id)]
        defaults = self.env['account.analytic.default'].search(domain)
        action = self.env.ref(
            'analytic.action_account_analytic_account_form').read()[0]
        if len(defaults) > 1:
            action['domain'] = [('id', 'in', defaults.ids)]
        elif len(defaults) == 1:
            form_view_name = 'analytic.view_account_analytic_account_form'
            action['views'] = [
                (self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = defaults.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
