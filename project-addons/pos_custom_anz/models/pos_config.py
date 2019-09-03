# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _compute_company_partner(self):
        for config in self:
            company_partner = config.stock_location_id.get_warehouse().partner_id
            config.company_partner = company_partner
            config.company_partner_phone = company_partner.phone or config.company_id.phone
            config.company_partner_name = company_partner.name or config.company_id.name
            config.company_partner_vat = company_partner.vat or config.company_id.vat
            config.company_partner_email = company_partner.email or config.company_id.email
            config.company_partner_web = company_partner.website or config.company_id.website
            config.company_partner_contact_address = company_partner.contact_address or config.company_id.contact_address
            config.company_partner_logo = company_partner.image or config.company_id.logo

    company_partner = fields.Many2one('res.partner', compute='_compute_company_partner', multi=True)
    company_partner_phone = fields.Char(compute='_compute_company_partner', multi=True)
    company_partner_name = fields.Char(compute='_compute_company_partner', multi=True)
    company_partner_vat = fields.Char(compute='_compute_company_partner', multi=True)
    company_partner_email = fields.Char(compute='_compute_company_partner', multi=True)
    company_partner_web = fields.Char(compute='_compute_company_partner', multi=True)
    company_partner_contact_address = fields.Char(compute='_compute_company_partner', multi=True)
    company_partner_logo = fields.Binary(compute='_compute_company_partner', multi=True)
