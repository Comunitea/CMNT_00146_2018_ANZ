# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.osv import expression

class PaymentTermRule(models.Model):

    _name = "payment.term.rule"


    partner_id = fields.Many2one('res.partner', string="Applied on", domain=[('payment_term_id', '!=', False)])
    old_payment_term_id = fields.Many2one('account.payment.term', string='Old pay. term')
    new_payment_term_id = fields.Many2one('account.payment.term', string='New pay. term')
    amount = fields.Float('From amount')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)


    def get_payment_term_rule(self, invoice):

        domain = expression.normalize_domain(['|', ('company_id', '=', invoice.company_id.id), ('company_id', '=', False)])

        if invoice.partner_id:
            domain = expression.AND([domain, ['|', ('partner_id', '=', invoice.partner_id.id), ('partner_id', '=', False)]])

        if invoice.payment_term_id:
            domain = expression.AND([domain, [('old_payment_term_id', '=', invoice.payment_term_id.id)]])

        domain = expression.AND([domain, [('amount', '<', invoice.amount_total)]])

        rule = self.search(domain, order='company_id asc, partner_id asc, amount desc')

        if not rule:
            message = _('Not found term rule for: Comapany: {}, Customer: {}, Payment {}, Amount {}'.format(
                                    invoice.company_id.name,
                                    invoice.partner_id.name,
                                    invoice.payment_term_id.name,
                                    invoice.amount_total))
            return False

        rule = rule[0]
        return rule
