# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SettlementLine(models.Model):
    _inherit = 'sale.commission.settlement.line'

    invoice = fields.Many2one(store=True)
    partner_id = fields.Many2one('res.partner', 
                                 related='invoice.partner_id', store=True)
    commission = fields.Many2one(store=True)


class Settlement(models.Model):
    _inherit = 'sale.commission.settlement'

    state = fields.Selection(selection_add=[('validated', 'Validated')])
    invoice_count = fields.Integer('Invoices',
                                   compute='_count_invoices')
    lines_count = fields.Integer('Líneas liq.',
                                 compute='_count_lines')

    @api.multi
    def _count_invoices(self):
        for sett in self:
            sett.invoice_count = len(sett.lines.mapped('invoice'))

    @api.multi
    def _count_lines(self):
        for sett in self:
            sett.lines_count = len(sett.lines)

    @api.multi
    def action_validate(self):
        self.write({'state': 'validated'})

    @api.multi
    def action_back(self):
        self.write({'state': 'settled'})

    @api.multi
    def view_settlement_lines(self):
        lines = self.lines
        action = self.env.ref(
            'custom_commission_anz.action_settle_line').read()[0]
        if len(lines) >= 1:
            action['domain'] = [('id', 'in', lines.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def view_invoices(self):
        invoices = self.lines.mapped('invoice')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
