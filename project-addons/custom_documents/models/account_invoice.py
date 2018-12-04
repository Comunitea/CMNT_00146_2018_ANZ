# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def lines_grouped_by_sale(self, group_templates):
        """This prepares a data structure for printing the invoice report
        grouped by sale."""
        self.ensure_one()
        lines_by_sale = {}
        if group_templates:
            lines = self.template_lines
        else:
            lines = self.invoice_line_ids
        for line in lines:
            if line.order_id not in lines_by_sale:
                lines_by_sale[line.order_id] = line
            else:
                lines_by_sale[line.order_id] += line
        return lines_by_sale


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    order_id = fields.Many2one('sale.order', related='sale_line_ids.order_id', store=True)


class AccountInvoiceLineTemplate(models.Model):
    _inherit = 'account.invoice.line.template'

    order_id = fields.Many2one('sale.order', readonly=True)

    def _select(self):
        select_str = super()._select()
        select_str += ', l.order_id as order_id'
        return select_str

    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += ', l.order_id'
        return group_by_str
