# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    is_player_boot = fields.Boolean("Bota de jugador")
    date_order = fields.Datetime(related="order_id.date_order")

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.order_id.partner_id and self.order_id.partner_id.player and self.product_id:
            partner = self.order_id.partner_id
            self.is_player_boot = not partner.color_type or \
                                  (partner.color_type and self.product_id.product_color == partner.color_type) and \
                                  partner.boot_type and  \
                                  partner.boot_type == self.product_id.boot_type
            self.discount = 100.00
        return result

