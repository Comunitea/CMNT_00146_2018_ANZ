# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools.misc import formatLang


class SaleOrderLineTemplateGroup(models.Model):

    _name = "sale.order.line.template.group"
    _description = "Sales order line group by template"
    _auto = False
    _rec_name = 'line_name'
    _order = 'sequence, product_tmpl_id'

    @api.multi
    @api.depends('product_tmpl_id')
    def get_line_name(self):
        for line in self:
            line.line_name = "{} {}".format(line.product_tmpl_id.name, line.variant_suffix)

    def _compute_line_reference(self):
        for line in self:
            lines = line._get_order_lines()
            if len(lines) == 1:
                line.product_ref = lines.product_id.default_code
            else:
                line.product_ref = lines[0].product_id.default_code[:-1]

    name = fields.Char('Order Reference', readonly=True)
    order_id = fields.Many2one('sale.order')
    line_name = fields.Char('Line name', compute="get_line_name")
    product_ref = fields.Char('referenece', compute='_compute_line_reference')

    date = fields.Datetime(string='Date Order', readonly=True)
    confirmation_date = fields.Datetime(string='Confirmation Date', readonly=True)
    sequence = fields.Integer(string="sequence")

    variant_suffix = fields.Char(related='product_tmpl_id.variant_suffix')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)
    product_uom_qty = fields.Float('Qty Ordered', readonly=True)
    qty_delivered = fields.Float('Qty Delivered', readonly=True)
    qty_to_invoice = fields.Float('Qty To Invoice', readonly=True)
    qty_invoiced = fields.Float('Qty Invoiced', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    price_total = fields.Float('Total', readonly=True)
    price_subtotal = fields.Float('Untaxed Total', readonly=True)
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), readonly=True)
    price_unit = fields.Float(digits=dp.get_precision('Product Price'), readonly=True)
    amt_to_invoice = fields.Float('Amount To Invoice', readonly=True)
    amt_invoiced = fields.Float('Amount Invoiced', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    tax_id = fields.Many2many('account.tax', compute='_compute_taxes')

    nbr = fields.Integer('# of Lines', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)
    team_id = fields.Many2one('crm.team', 'Sales Channel', readonly=True, oldname='section_id')
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True)
    weight = fields.Float('Gross Weight', readonly=True)
    volume = fields.Float('Volume', readonly=True)
    idlist = fields.Char(readonly=True)

    def _select(self):
        select_str = """
        WITH currency_rate as (%s)
             SELECT min(l.id) as id,
                    string_agg(l.id::text, ',') as idlist,
                    min(l.sequence) as sequence,
                    l.product_tmpl_id as product_tmpl_id,
                    count(*) as nbr,
                    l.product_uom as product_uom,
                    COALESCE(l.discount, 0) as discount,
                    l.order_id as order_id,
                    s.name as name,
                    s.date_order as date,
                    s.confirmation_date as confirmation_date,
                    s.state as state,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    t.categ_id as categ_id,
                    sum(l.product_uom_qty) as product_uom_qty,
                    sum(l.qty_delivered) as qty_delivered,
                    sum(l.qty_invoiced) as qty_invoiced,
                    sum(l.qty_to_invoice) as qty_to_invoice,
                    sum(l.price_total) as price_total,
                    sum(l.price_subtotal) as price_subtotal,
                    sum(l.amt_to_invoice) as amt_to_invoice,
                    sum(l.amt_invoiced) as amt_invoiced,
                    sum(p.weight * l.product_uom_qty) as weight,
                    sum(p.volume * l.product_uom_qty) as volume,
                    l.price_unit as price_unit,
                    extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    s.pricelist_id as pricelist_id,
                    s.analytic_account_id as analytic_account_id,
                    s.team_id as team_id
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
                sale_order_line l
                    join sale_order s on (l.order_id=s.id)
                    left join product_product p on (l.product_id=p.id)
                    left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                    left join currency_rate cr on (cr.currency_id = pp.currency_id and
                        cr.company_id = s.company_id and
                        cr.date_start <= coalesce(s.date_order, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
        """
        return from_str

    def _where(self):
        where = """
            l.order_id in {}
        """.format(self._context('template_line_domain', []))
        return where

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_tmpl_id,
                     l.discount,
                     l.product_uom,
                     t.uom_id,
                     l.order_id,
                     l.price_unit,
                     t.categ_id,
                        s.name,
                        s.date_order,
                        s.confirmation_date,
                        s.partner_id,
                        s.user_id,
                        s.state,
                        s.company_id,
                        s.pricelist_id,
                        s.analytic_account_id,
                        s.team_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql = """CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by())

        self.env.cr.execute(sql)

    @api.multi
    def write(self, vals):

        if 'sequence' in vals:
            self._get_order_lines().write({'sequence': vals['sequence']})
            vals.pop('sequence')
        if vals:
            return super(SaleOrderLineTemplateGroup, self).write(vals)

    def _get_order_lines(self):
        return self.env['sale.order.line'].browse(list(map(int, self.idlist.split(','))))

    def get_name(self):
        line = self._get_order_lines()
        if len(line) == 1:
            att_tag = line.product_id.attribute_value_ids
            if att_tag:
                return self.product_tmpl_id.name + ' - ' + att_tag.name_get()[0][1]
        return self.product_tmpl_id.name

    def get_qties(self):
        lines = self._get_order_lines()
        if len(lines) == 1:
            return [formatLang(self.env, lines.product_uom_qty)]
        qties_list = []
        for line in lines:
            qty_str = ''
            att_tag = line.product_id.attribute_value_ids
            if att_tag:
                qty_str = att_tag.name_get()[0][1]
            qty_str += ' - ' + formatLang(self.env, line.product_uom_qty)
            qties_list.append(qty_str)
        return qties_list

    def _compute_taxes(self):
        for template_line in self:
            line = template_line._get_order_lines()
            if len(line) == 1:
                template_line.tax_id = line.tax_id
            else:
                template_line.tax_id = line[0].tax_id
