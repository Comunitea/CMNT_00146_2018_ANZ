# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    associate_id = fields.Many2one(
        'res.partner', 'Associate',
        domain=[('customer', '=', True)]
    )

    @api.multi
    def _create_picking(self):
        """
        Avoid create picking when associated id
        """
        self2 = self.filtered(lambda p: not p.associate_id)
        return super(PurchaseOrder, self2)._create_picking()
        return True

    @api.multi
    def action_view_invoice(self):
        '''
        Create invoice with the associate
        '''
        res = super(PurchaseOrder, self).action_view_invoice()
        res['context']['default_associate_id'] = self.associate_id.id
        return res
