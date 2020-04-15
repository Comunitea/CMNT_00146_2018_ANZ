# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # NOT A REAL PROPERTY !!!!
    property_product_pricelist = fields.Many2one(website_dependent=True)

    @api.one
    def _inverse_product_pricelist(self):
        """
        Workaround to pass website_id on context.
        It is necessary if you have different pricelists on the same website.
        Website_id will be cached by context on web_website module from ITP Projects.
        """
        pls = self.env['product.pricelist'].search(
            [('country_group_ids.country_ids.code', '=', self.country_id and self.country_id.code or False)],
            limit=1
        )
        default_for_country = pls and pls[0]
        actual = self.env['ir.property'].get('property_product_pricelist', 'res.partner', 'res.partner,%s' % self.id)

        # update at each change country, and so erase old pricelist
        if self.property_product_pricelist or (actual and default_for_country and default_for_country.id != actual.id):
            # keep the company of the current user before sudo
            website_id = self._context.get('website_id') or self.env.user.backend_website_id.id
            self.env['ir.property'].with_context(force_company=self.env.user.company_id.id, website_id=website_id).sudo().set_multi(
                'property_product_pricelist',
                self._name,
                {self.id: self.property_product_pricelist or default_for_country.id},
                default_value=default_for_country.id
            )
