# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models, fields, _
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _compute_sale_order_line_count(self):
        for order in self:
            order.sale_order_line_count = len(order.order_line)

    sale_order_line_count = fields.Integer('Order line count', compute='_compute_sale_order_line_count')

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'type_id' in vals:
            sale_type = self.env['sale.order.type'].search_read([('id', '=', vals['type_id'])], fields=['operating_unit_id'])
            self.order_line.write({'operating_unit_id': sale_type and sale_type[0]['operating_unit_id'][0]})
        return res

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id_warning(self):
        """
        Same logic for warning as action_confirm method of partner_sale_risk
        module.
        """
        res = super(SaleOrder, self).onchange_partner_id_warning()

        if not self.partner_id:
            return
        if not res:
            res = {}
        partner = self.partner_id
        exception_msg = ''
        if partner.risk_exception:
            exception_msg += _("Financial risk exceeded.\n")
        elif partner.risk_sale_order_limit and (
                (partner.risk_sale_order + self.amount_total) >
                partner.risk_sale_order_limit):
            exception_msg += _(
                "This sale order exceeds the sales orders risk.\n")
        elif partner.risk_sale_order_include and (
                (partner.risk_total + self.amount_total) >
                partner.credit_limit):
            exception_msg += _(
                "This sale order exceeds the financial risk.\n")
        if exception_msg:
            title = ("Risk exceded for %s") % partner.name
            message = exception_msg
            warning = {
                    'title': title,
                    'message': message,
            }
            res['warning'] = warning
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    operating_unit_id = fields.Many2one('operating.unit', string="Operating unit")
    virtual_stock_conservative = fields.Float(related="product_id.virtual_stock_conservative",
                                              string='Virtual Stock Conservative')

    requested_date = fields.Date('Requested Date')
    ref_change = fields.Boolean('Reference change')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.order_id.type_id:
            self.operating_unit_id = self.order_id.type_id.operating_unit_id
        # Check if product added is restricted by brand.
        # If restricted sets true ref_check field
        if self._context.get('ref_change_partner_id', False):
            partner_id = self._context.get('ref_change_partner_id', False)
            partner = self.env['res.partner'].browse(partner_id)
            if partner.allowed_brand_ids:
                brand_id = self.product_id.product_brand_id.id if \
                    self.product_id.product_brand_id else \
                    self.product_tmpl_id.product_brand_id.id
                if not brand_id:
                    self.ref_change = True
                    return result
                if brand_id not in \
                        partner.allowed_brand_ids.ids:
                    self.ref_change = True
                else:
                    self.ref_change = False
        return result

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Propagate ref_check field, to account_invoice_line
        """
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update(ref_change=self.ref_change)
        return res
