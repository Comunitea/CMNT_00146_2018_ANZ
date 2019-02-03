# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProductBrand(models.Model):

    _inherit = 'product.brand'

    @api.multi
    def _count_commissions(self):
        for brand in self:
            domain = ['|', ('brand_id', '=', brand.id),
                      ('brand_id', '=', False)]
            count = self.env['commission.brand'].search_count(domain)
            brand.commission_rules_count = count

    commission_rules_count = fields.Integer('# Commissions',
                                            compute='_count_commissions')

    @api.multi
    def action_view_commissions(self):
        self.ensure_one()
        domain = ['|', ('brand_id', '=', self.id),
                  ('brand_id', '=', False)]
        commission_rules = self.env['commission.brand'].search(domain)
        action = self.env.ref(
            'custom_commission_anz.action_commission_by_brand').read()[0]
        action['domain'] = [('id', 'in', commission_rules.ids)]
        action['context'] = {'default_brand_id': self.id,
                             'search_default_brand_id': self.id}
        return action
