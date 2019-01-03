# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api

class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    is_player_boot = fields.Boolean("Bota de jugador")
    date_order = fields.Datetime(related="order_id.date_order")
    virtual_stock_conservative = fields.Float(related="product_id.virtual_stock_conservative",
                                              string='Virtual Stock Conservative', related_sudo=True)


    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        self.is_player_boot = False
        if self.product_id and self.order_id.partner_id and self.order_id.partner_id.player and self.order_id.partner_id.boot_type and self.order_id.partner_id.color_type:
            partner = self.order_id.partner_id
            self.is_player_boot = self.product_id.boot_type == partner.boot_type and self.product_id.product_color == partner.color_type

            if self.is_player_boot:
                self.discount = 100.00

        return result
