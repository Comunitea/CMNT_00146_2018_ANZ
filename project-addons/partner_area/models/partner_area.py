# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class ResPartnerArea(models.Model):

    _name = 'res.partner.area'
    _parent_name = "area_id"
    _parent_store = True

    @api.multi
    def get_sub_partners(self):
        for area in self:
            area.sub_partner_ids = area.child_ids.mapped('partner_ids')
            area.partner_ids = area.area_partner_ids + area.sub_partner_ids

    name = fields.Char("Partner area", required=True)
    complete_name = fields.Char("Full area Name", compute='_compute_complete_name', store=True)
    code = fields.Char("Partner area code")
    state_ids = fields.Many2many('res.country.state',
                                    "res_partner_area_states_rel",
                                    "res_partner_area_id",
                                    "state_id",
                                    string="States in area"
    )

    active = fields.Boolean('Active', default=True, help="By unchecking the active field, you may hide a partner area without deleting it.")
    area_id = fields.Many2one('res.partner.area', string="Parent area", index=True, ondelete='cascade')
    area_partner_ids = fields.One2many('res.partner', 'area_id', string="Partners")
    sub_partner_ids = fields.One2many('res.partner', compute="get_sub_partners")
    partner_ids = fields.One2many('res.partner', compute="get_sub_partners")
    child_ids = fields.One2many('res.partner.area', 'area_id', string="Childs area")
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)

    @api.one
    @api.depends('name', 'area_id.complete_name')
    def _compute_complete_name(self):
        """ Forms complete name of area from parent area to child area. """
        if self.area_id.complete_name:
            self.complete_name = '%s/%s' % (self.area_id.complete_name, self.name)
        else:
            self.complete_name = self.name

    def write(self, values):
        return super(ResPartnerArea, self).write(values)


    def name_get(self):
        ret_list = []
        for area in self:
            orig_area = area
            name = area.name
            while area.area_id:
                area = area.area_id
                if not name:
                    raise UserError(_('You have to set a name for this area.'))
                name = area.name + "/" + name
            ret_list.append((orig_area.id, name))
        return ret_list

