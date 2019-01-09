# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models, fields


class StockBatchPicking(models.Model):

    _inherit = 'stock.batch.picking'

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True)

