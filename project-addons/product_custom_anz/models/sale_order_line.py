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
        if self.product_id and self.order_id.partner_id and self.order_id.partner_id.player and self.order_id.product_id in self.order_id.partner_id.allowed_boot_ids:
            self.is_player_boot = True
            self.discount = 100.00
        else:
            self.is_player_boot = False
        return result

