# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.exceptions import UserError,ValidationError


class ResPartnerArea(models.Model):
    _inherit = 'res.partner.area'

    allowed_brand_ids = fields.Many2many('product.brand',
                                         "allowed_res_partner_area_product_brand_rel",
                                         "res_partner_area_id",
                                         "product_brand_id",
                                         string="Allowed brands for this partner",
                                         help="If empty, all brands"
                                         )
    restricted_brand_ids = fields.Many2many('product.brand',
                                            "restrict_res_partner_area_product_brand_rel",
                                            "res_partner_area_id",
                                            "product_brand_id",
                                            string="Restricted brands for this partner"
                                            )

class ResPartner(models.Model):

    _inherit = 'res.partner'

    affiliate = fields.Boolean('Affiliate')
    player = fields.Boolean('Player')
    sponsorship_bag = fields.Float()
    analytic_default_count = fields.Integer('Analytic Defaults',
                                            compute='_count_analytic_defaults')
    allowed_brand_ids = fields.Many2many('product.brand',
                                        "allowed_res_partner_product_brand_rel",
                                        "res_partner_id",
                                        "product_brand_id",
                                        string="Allowed brands for this partner",
                                        help="If empty, all brands"
                                    )
    restricted_brand_ids = fields.Many2many('product.brand',
                                         "restrict_res_partner_product_brand_rel",
                                         "res_partner_id",
                                         "product_brand_id",
                                         string="Restricted brands for this partner"
                                         )

    allowed_categories_ids = fields.Many2many('product.category',
                                         "allowed_res_partner_product_category_rel",
                                         "res_partner_id",
                                         "product_category_id",
                                         string="Allowed categories for this partner",
                                         help="If empty, all categories"
                                         )
    restricted_categories_ids = fields.Many2many('product.category',
                                            "restrict_res_partner_product_category_rel",
                                            "res_partner_id",
                                            "product_category_id",
                                            string="Restricted categories for this partner"
                                            )
    ref = fields.Char(default='[Auto]')

    risk_exception = fields.Boolean(search="_search_risk_exception")

    @api.multi
    def refresh_partner_ref(self):
        partner_sequence = self.env['ir.sequence'].search([('code', '=', 'auto_partner')])
        if partner_sequence:
            for partner in self:
                seq = partner_sequence.next_by_id()
                zip_str = partner.zip or partner.parent_id and partner.parent_id.zip or '00'
                zip_str = zip_str[0:2]
                type_str = partner.type[0:2].upper()
                partner.ref = '{}{}{}'.format(type_str, zip_str, seq)

    @api.model
    def create(self, vals):
        # Check if sequence exists for specific country, and get a new number
        partner = super(ResPartner, self).create(vals)
        if vals.get('ref', '[Auto]') == '[Auto]':
            partner.refresh_partner_ref()
        return partner

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'ref' in vals and not vals['ref']:
            self.refresh_partner_ref()
        return res

    def get_partner_by_context(self):
        partner = self._context.get('partner_id', False) and \
                  self.env['res.partner'].\
                  browse(self._context.get('partner_id')).\
                  commercial_partner_id or \
                  self.env.user.partner_id.commercial_partner_id
        return partner

    def add_args_to_product_search(self, args=[]):

        args = expression.normalize_domain(args)

        if self.area_id:
            area_domain = [('product_brand_id.restricted_area_ids', 'not in', [self.area_id.id])]
            args = expression.AND([args, area_domain])

        # Si el partner tiene marcas permitidas, se usan las del partner, si no las de la zona
        allowed_brand_ids = self.allowed_brand_ids.ids or self.area_id.allowed_brand_ids.ids or []
        # Las restriccionees de las marcas se suma SIEMPRE
        restricted_brand_ids = self.restricted_brand_ids.ids + self.area_id.restricted_brand_ids.ids

        if allowed_brand_ids and restricted_brand_ids:
            [allowed_brand_ids.remove(i) for i in restricted_brand_ids if i in allowed_brand_ids]
        if allowed_brand_ids:
            args = expression.AND([args, ['|', ('product_brand_id', '=', False), ('product_brand_id', 'in', allowed_brand_ids)]])
        elif restricted_brand_ids:
            args = expression.AND([args, ['|', ('product_brand_id', '=', False),('product_brand_id', 'not in', restricted_brand_ids)]])
        args = expression.normalize_domain(args)
        if self.allowed_categories_ids or self.restricted_categories_ids:
            a_categ = []
            r_categ = []
            for categ in self.allowed_categories_ids:
                a_categ += categ.search([('id', 'child_of', categ.id)]).ids
            for categ in self.restricted_categories_ids:
                r_categ += categ.search([('id', 'child_of', categ.id)]).ids

            if a_categ and r_categ:
                [a_categ.remove(i) for i in r_categ if i in a_categ]
            if a_categ:
                args = expression.AND([args, ['|', ('categ_id', '=', False), ('categ_id', 'in', a_categ)]])
            elif r_categ:
                args = expression.AND([args, [('categ_id', 'not in', r_categ)]])
            args = expression.normalize_domain(args)
        #print (args)
        return args

    @api.multi
    def _count_analytic_defaults(self):
        for partner in self:
            domain = [('partner_id', '=', partner.id)]
            count = self.env['account.analytic.default'].search_count(domain)
            partner.analytic_default_count = count

    @api.multi
    def view_analytic_defaults(self):
        self.ensure_one()
        domain = [('partner_id', '=', self.id)]
        defaults = self.env['account.analytic.default'].search(domain)
        action_name = 'account_analytic_default.action_analytic_default_list'
        action = self.env.ref(
            action_name).read()[0]
        if len(defaults) > 1:
            action['domain'] = [('id', 'in', defaults.ids)]
        elif len(defaults) == 1:
            form_view_name = \
                'account_analytic_default.view_account_analytic_default_form'
            action['views'] = [
                (self.env.ref(form_view_name).id, 'form')]
            action['res_id'] = defaults.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def decrease_bag(self, amount):
        if amount < 0.0:
            self.sponsorship_bag += abs(amount)
        elif amount <= self.sponsorship_bag:
            self.sponsorship_bag -= amount
        elif amount > self.sponsorship_bag:
            raise UserError(_('You try to sponsorship a quantity of %s and \
                the rest of the bag is %s.') % (amount, self.sponsorship_bag))


    def _search_risk_exception(self,operator,value):
        """ """
        if operator == '=' and isinstance(value, (int)):
            id_list = [company.id for company in self.env['res.partner'].search([('is_company','=',True)]) if company.risk_exception == value]
            return [('id','in',id_list)]
        else:
            ValidationError('The field risk_exception is not searchable '
                            'with the operator {} and value {}'.format(operator,value))

