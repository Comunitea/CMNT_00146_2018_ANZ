# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval

class YesNoConfirmation(models.TransientModel):
    _name = 'yesno.confirmation'

    question = fields.Text("Question")
    function = fields.Text("Function")
    ctx = fields.Text("Context")
    object = fields.Text('Object')
    model_id = fields.Many2one('ir.model', "Model")
    return_id = fields.Integer()

    @api.multi
    def confirm(self):

        old_ctx = self.env.context.get('old_ctx', {})
        old_ctx.update(yes_confirmation=True, return_id=self.return_id)
        vals = {'name': 'name_wzd',
                'model_id': self.model_id.id,
                'state': 'code',
                'code': 'model.{}'.format(self.function)}
        new_server_action = self.env['ir.actions.server'].with_context(old_ctx).new(vals)
        res = new_server_action.run()
        if self.env.context.get('delete', True):
            self.env.cr.execute('delete from yesno_confirmation')
        return res

    def return_wzd(self, model, values):
        ctx = self._context.get('model_context', {})
        values.update(object=model._name,
                      ctx=ctx,
                      return_id=model.id,
                      model_id=model.env['ir.model'].search([('model', '=', model._name)]).id)
        print (values)
        yesno = self.env['yesno.confirmation'].create(values)
        return {
            'name': values['name'],
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'yesno.confirmation',
            'target': 'new',
            'res_id': yesno.id,
            'context': dict(ctx)}