# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ProductLabelPricelist(models.TransientModel):
    _name = 'product.product.label'

    barcode = fields.Char()
    name = fields.Char()
    price = fields.Float()
    lst_price = fields.Float()
    attr_name = fields.Char()
    height_r = fields.Integer()
    height_t= fields.Integer()
    rows = fields.Integer()
    discount = fields.Boolean('Is discount?', default=False)

class ProductLabelPricelist(models.TransientModel):
    _name = 'product.label.pricelist'
    _description = 'Label Price List'

    price_list = fields.Many2one('product.pricelist', 'Tarifa', required=True)
    discount = fields.Boolean('Is discount?', default=False)
    altura = fields.Integer(default=110)
    anchura = fields.Integer(default=350)
    baseincrement = fields.Integer('% añadido al precio base: ', default = 0)
    taxes = fields.Boolean('Add taxes', default=True)

    @api.multi
    def print_report(self):

        ppl = self.env['product.product.label']
        ctx = self._context.copy()
        if self.price_list:
            ctx.update(pricelist=self.price_list.id)
        res = self.with_context(ctx).env['product.product'].\
            browse(self._context.get('active_ids', []))
        p_ids = []
        h = self.altura
        if self.discount:
            rows = 4
        else:
            rows = 3
        for p in res:
            price = p.price
            lst_price = p.lst_price if not self.discount else \
                p.lst_price * (1 + self.baseincrement/100)
            if self.taxes:
                company = self.env['res.company']._company_default_get()
                price_tax = p.taxes_id.compute_all(
                    price, company.currency_id, 1, product=p)
                price_lst_tax = p.taxes_id.compute_all(
                    price, company.currency_id, 1, product=p)
                price = price_tax['total_included']
                lst_price = price_lst_tax['total_included']

            vals = {
                'name': p.product_tmpl_id.ref_template or
                p.product_tmpl_id.default_code,
                'barcode': p.barcode,
                'attr_name': p.attribute_value_ids and
                p.attribute_value_ids[0].name or 'Única',
                'price': price,
                'lst_price': lst_price,
                'height_r': h / rows,
                'height_t': h,
                'discount': self.discount,
                'rows': rows,
                'width': self.anchura
            }
            print(vals)
            p_id = ppl.create(vals).id
            p_ids.append(p_id)

        return self.env.ref(
            'product_custom_label_anz.action_print_label_docs_pricelist').\
            report_action(ppl.browse(p_ids))
