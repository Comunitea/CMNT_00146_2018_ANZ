# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models, fields
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    @api.depends('move_line_ids')
    def _compute_move_line_ids_count(self):
        for pick in self:
            pick.move_line_ids_count = len(pick.move_line_ids)


    move_line_ids_count = fields.Integer(
        'Template line count', compute='_compute_move_line_ids_count')

    @api.multi
    def action_view_move_lines(self):

        self.ensure_one()
        if (self.picking_type_code in ('incoming', 'outgoing') and not self.partner_id) or not self.company_id.id:
            raise ValidationError('Revisa los campos cliente, tarifa, compañia y tipo de venta')

        model_data = self.env['ir.model.data']
        tree_view = model_data.get_object_reference(
            'picking_move_line_ids_tree', 'pick_move_line_ids_tree_view')

        action = self.env.ref(
            'picking_move_line_ids_tree.pick_move_line_ids_tree_view_action').read()[0]

        action['views'] = {
            (tree_view and tree_view[1] or False, 'tree')}

        action['domain'] = [('picking_id', '=', self.id)]

        action['context'] = {
            'default_picking_id': self.id,
            'partner_id': self.partner_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
            'picking_type_code': self.picking_type_code,
            'show_lots_text': self.show_lots_text
        }
        # action['view_ids'] = [tree_view and tree_view[1]]
        return action



