# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    affiliate = fields.Boolean('Affiliate')
    player = fields.Boolean('Player')
    analytic_default_count = fields.Integer('Analytic Defaults',
                                            compute='_count_analytic_defaults')
    boot_type = fields.Many2one('product.attribute.value', 'Type of boot',
                                domain=[('is_tboot', '=', True)])
    color_type = fields.Many2one('product.attribute.value', 'Type of color',
                                 domain=[('is_color', '=', True)])
    

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
        action_name = 'account_analytic_default.action_analytic_default_list'
        action = self.env.ref(
            action_name).read()[0]
        if len(defaults) > 1:
            action['domain'] = [('id', 'in', defaults.ids)]
        elif len(defaults) == 1:
            form_view_name = 'account.analytic.default.form'
            action['views'] = [
                (self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = defaults.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
