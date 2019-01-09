# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _invoice_line_count(self):
        r = {}
        if not self.user_has_groups('account.group_account_user'):
            return r

        for product in self:
            domain=[('product_id', '=', product.id), ('invoice_id.state', 'in', ('open', 'paid'))]
            product.invoice_line_count = self.env['account.invoice.line'].search_count(domain)

    invoice_line_count = fields.Integer(compute='_invoice_line_count', string='# Invoice line')


