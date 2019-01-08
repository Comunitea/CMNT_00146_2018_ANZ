# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    def get_boot_ids(self):
        order_line_ids = self.env['sale.order.line']
        for player in self.filtered(lambda x: x.player):
            domain = [('order_id.partner_id', '=', player.id), ('product_id.boot_type', '!=', False)]
            player.boot_ids = [(6, 0, order_line_ids.search(domain).ids)]
            player.boot_ids_count = sum(x.qty_delivered for x in player.boot_ids)

    show_pvp = fields.Boolean('Show PVP')
    boot_type = fields.Many2one('product.attribute.value', 'Type of boot',
                                domain=[('is_tboot', '=', True)])
    color_type = fields.Many2one('product.attribute.value', 'Type of color',
                                 domain=[('is_color', '=', True)])
    size_type_ids = fields.Many2many('product.attribute.value', string='Size',domain=[('is_color', '!=', True), ('is_tboot', '!=', True)])
    allowed_boot_ids = fields.Many2many('product.product', string='Allowed boots')#, domain=[('product_tmpl_id.boot_type', '=', False)])
    boot_ids = fields.One2many('sale.order.line', string="Histórico", compute="get_boot_ids")
    boot_ids_count = fields.Integer(string="Quantity", compute="get_boot_ids")


    def add_args_to_product_search(self, args=[]):
        return super(ResPartner, self).add_args_to_product_search(args=args)
