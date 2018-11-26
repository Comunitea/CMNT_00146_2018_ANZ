# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError


class PromotionsRulesConditionsExprs(models.Model):

    _inherit = 'promos.rules.conditions.exps'

    attribute = fields.Selection(selection_add=[('brand',
                                                 'Product Brand')])

    @api.onchange('attribute')
    def on_change_attribute(self):
        """
        Set the value field to the format if nothing is there
        """
        res = super(PromotionsRulesConditionsExprs, self).on_change_attribute()
        if self.attribute == 'brand':
            self.value = "'product_brand'"
        return res

    def validate(self, vals):
        """
        Set the value field to the format if nothing is there
        """
        res = super(PromotionsRulesConditionsExprs, self).validate(vals)
        iterator_comparators = ['in', 'not in']
        attribute = vals['attribute']
        comparator = vals['comparator']
        # Mismatch 6:
        if attribute == 'brand' and comparator not in iterator_comparators:
            raise UserError("Only %s can be used with Product Brand"
                            % ",".join(iterator_comparators))
        return res

    def serialise(self, attribute, comparator, value):
        """
        Using kwargs to evaluate if product has a specific mark
        """
        if attribute == 'brand':
            return "%s %s kwargs['product_brands']" % (value, comparator)
        return super(PromotionsRulesConditionsExprs, self).serialise(
                attribute, comparator, value)

    def serialise_pos(self, attribute, comparator, value):
        """
        Using kwargs to evaluate if product has a specific mark
        """
        if attribute == 'brand':
            if comparator == 'in':
                return "%s %s product_brands" % (value, comparator)
            else:
                return "!(%s in product_brands)" % (value)
        return super(PromotionsRulesConditionsExprs, self).serialise_pos(
                attribute, comparator, value)

    def evaluate(self, order):
        # Get order lines products brands
        product_brands = []
        for line in order.order_line:
            if line.product_id.product_brand_id:
                if line.product_id.product_brand_id.name not in product_brands:
                    product_brands.append(
                        line.product_id.product_brand_id.name)
        # Using kwargs to evaluate the serialiced expression
        res = super(PromotionsRulesConditionsExprs, self).\
            evaluate(order, product_brands=product_brands)
        return res
