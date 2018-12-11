# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _
from odoo.exceptions import UserError

# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.osv import expression

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

    @api.multi
    def get_boot_ids(self):
        order_line_ids = self.env['sale.order.line']
        for player in self.filtered(lambda x: x.player):
            domain = [('order_id.partner_id', '=', player.id), ('product_id.boot_type', '!=', False)]
            player.boot_ids = [(6, 0, order_line_ids.search(domain).ids)]
            player.boot_ids_count = sum(x.qty_delivered for x in player.boot_ids)


    affiliate = fields.Boolean('Affiliate')
    player = fields.Boolean('Player')
    sponsorship_bag = fields.Float()
    analytic_default_count = fields.Integer('Analytic Defaults',
                                            compute='_count_analytic_defaults')
    boot_type = fields.Many2one('product.attribute.value', 'Type of boot',
                                domain=[('is_tboot', '=', True)])
    color_type = fields.Many2one('product.attribute.value', 'Type of color',
                                 domain=[('is_color', '=', True)])
    boot_ids = fields.One2many('sale.order.line', string="Histórico", compute="get_boot_ids")
    boot_ids_count = fields.Integer(string="Quantity", compute="get_boot_ids")


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


    def get_partner_by_context(self):
        partner = self._context.get('partner_id', False) and \
                  self.env['res.partner'].browse(self._context.get('partner_id')) or\
                  self.env.user.partner_id
        return partner

    @api.model
    def add_args_to_product_search(self, args=[]):

        if not self.customer:
            return args
        # De momento no se usa las zonas en los productos
        if self.area_id and False:
            args.append((('allowed_area_ids', 'in', self.area_id.id)))
            args.append((('restrict_area_ids', 'not in', self.area_id.id)))

        # Si el partner tiene marcas permitidas, se usan las del partner, si no las de la zona
        allowed_brand_ids = self.allowed_brand_ids.ids or self.area_id.allowed_brand_ids.ids or []
        # Las restriccionees de las marcas se suma SIEMPRE
        restricted_brand_ids = self.restricted_brand_ids.ids + self.area_id.restricted_brand_ids.ids

        if allowed_brand_ids and restricted_brand_ids:
            [allowed_brand_ids.remove(i) for i in restricted_brand_ids if i in allowed_brand_ids]
        if allowed_brand_ids:
            args = expression.AND([args, [('product_brand_id', 'in', allowed_brand_ids)]])
        elif restricted_brand_ids:
            args = expression.AND([args, [('product_brand_id', 'not in', restricted_brand_ids)]])

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
                args = expression.AND([args, [('categ_id', 'in', a_categ)]])
            elif r_categ:
                args = expression.AND([args, [('categ_id', 'not in', r_categ)]])

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
            form_view_name = 'account.analytic.default.form'
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

