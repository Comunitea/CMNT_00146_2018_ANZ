# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools.misc import formatLang


class AccountInvoiceLineTemplate(models.Model):
    _name = 'account.invoice.line.template'

    _auto = False

    idlist = fields.Char(readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    line_name = fields.Char('Line name', compute="_compute_line_name")
    product_ref = fields.Char('referenece', compute='_compute_line_reference')
    invoice_line_tax_ids = fields.Many2many(
        'account.tax', compute='_compute_taxes')
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure', readonly=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', readonly=True)
    invoice_id = fields.Many2one('account.invoice')
    quantity = fields.Float(readonly=True)
    price_total = fields.Float('Total', readonly=True)
    price_subtotal = fields.Float('Untaxed Total', readonly=True)
    price_unit = fields.Float(
        'unit price', readonly=True, digits=dp.get_precision('Product Price'))
    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'),
        readonly=True)
    ref_change = fields.Boolean()

    def _select(self):
        select_str = """
select min(l.id) as id,
       string_agg(l.id::text, ',') as idlist,
        count(*) as nbr,
        l.uom_id as product_uom,
        l.product_tmpl_id as product_tmpl_id,
        COALESCE(l.discount, 0) as discount,
        l.invoice_id as invoice_id,
        sum(l.quantity) as quantity,
        sum(l.price_total) as price_total,
        sum(l.price_subtotal) as price_subtotal,
        l.price_unit as price_unit,
        l.ref_change
        """
        return select_str

    def _from(self):
        from_str = """
account_invoice_line l
        """
        return from_str

    def _group_by(self):
        group_by_str = """
l.product_tmpl_id,
l.uom_id,
l.discount,
l.invoice_id,
l.price_unit,
l.ref_change

        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql = """CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s
            GROUP BY %s
            )""" % (self._table, self._select(), self._from(), self._group_by())
        self.env.cr.execute(sql)

    def _compute_line_name(self):
        for template_line in self:
            if template_line.ref_change:
                template_line.line_name = template_line.product_tmpl_id.ref_change_code
                continue
            line = template_line._get_invoice_lines()
            if len(line) == 1:
                if not template_line.product_tmpl_id or \
                        template_line.product_tmpl_id.type == 'service':
                    template_line.line_name = line.name
                    continue
                att_tag = line.product_id.attribute_value_ids
                if att_tag:
                    template_line.line_name = template_line.product_tmpl_id.name + ' - ' + att_tag.name_get()[0][1]
                    continue
            template_line.line_name = template_line.product_tmpl_id.name

    def _compute_line_reference(self):
        for line in self:
            lines = line._get_invoice_lines()
            if len(lines) == 1:
                line.product_ref = lines.product_id and lines.product_id.default_code or lines.name
            else:
                line.product_ref = lines[0].product_id.default_code[:-1]

    def _compute_taxes(self):
        for template_line in self:
            line = template_line._get_invoice_lines()
            if len(line) == 1:
                template_line.invoice_line_tax_ids = line.invoice_line_tax_ids
            else:
                template_line.invoice_line_tax_ids = line[0].invoice_line_tax_ids

    def _get_invoice_lines(self):
        return self.env['account.invoice.line'].browse(
            list(map(int, self.idlist.split(','))))

    def get_qties(self):
        lines = self._get_invoice_lines()
        if len(lines) == 1:
            return [formatLang(self.env, lines.quantity)]
        qties_list = []
        for line in lines:
            qty_str = ''
            att_tag = line.product_id.attribute_value_ids
            if att_tag:
                qty_str = att_tag.name_get()[0][1]
            qty_str += ' - ' + formatLang(self.env, line.quantity)
            qties_list.append(qty_str)
        return qties_list
