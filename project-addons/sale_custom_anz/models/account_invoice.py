# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    ref_change = fields.Boolean('Reference change')

