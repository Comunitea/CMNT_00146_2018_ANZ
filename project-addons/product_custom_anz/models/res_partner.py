# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError


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

    def add_args_to_product_search(self, args=[]):

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
            args.append((('product_brand_id', 'in', allowed_brand_ids)))
        elif restricted_brand_ids:
            args.append((('product_brand_id', 'not in', restricted_brand_ids)))


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
                args.append((('categ_id', 'in', a_categ)))
            elif r_categ:
                args.append((('categ_id', 'not in', r_categ)))

        return args