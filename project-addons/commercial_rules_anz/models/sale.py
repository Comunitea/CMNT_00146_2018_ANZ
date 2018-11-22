# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def action_confirm(self):
        """
        Apply promotions when confirm the order
        """
        self.apply_commercial_rules()
        return super(SaleOrder, self).action_confirm()

    def apply_commercial_rules(self):
        """
        Set delivery line, after Appling promotions
        """
        res = super(SaleOrder, self).apply_commercial_rules()
        if self. carrier_id:
            self.get_delivery_price()
            self.set_delivery_line()
        return res
