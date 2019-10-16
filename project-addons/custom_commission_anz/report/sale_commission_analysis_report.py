# © 2019 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class SaleCommissionAnalysisReport(models.Model):
    _inherit = "sale.commission.analysis.report"

    date_due = fields.Date('Date Due', readonly=True)

    def _select(self):
        select_str = """
            SELECT min(aila.id) as id, ai.partner_id partner_id,
            ai.state invoice_state,
            ai.date_invoice,
            ai.date_due,
            ail.company_id company_id,
            rp.id agent_id,
            pt.categ_id categ_id,
            ail.product_id product_id,
            pt.uom_id,
            ail.quantity,
            ail.price_unit,
            ail.price_subtotal,
            sc.fix_qty percentage,
            SUM(aila.amount) AS amount,
            ail.id invoice_line_id,
            aila.settled,
            aila.commission commission_id
        """
        return select_str

    def _group_by(self):
        group_by_str = """
            GROUP BY ai.partner_id,
            ai.state,
            ai.date_invoice,
            ai.date_due,
            ail.company_id,
            rp.id,
            pt.categ_id,
            ail.product_id,
            pt.uom_id,
            ail.quantity,
            sc.fix_qty,
            ail.id,
            aila.settled,
            aila.commission
        """
        return group_by_str