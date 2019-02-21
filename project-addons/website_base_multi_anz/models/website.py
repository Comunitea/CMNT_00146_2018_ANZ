# -*- coding: utf-8 -*-
#
# © 2018 Comunitea - Ruben Seijas <ruben@comunitea.com>
# © 2018 Comunitea - Pavel Smirnov <pavel@comunitea.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.seo_base.models.settings import _default_website


class Website(models.Model):
    _inherit = 'website'

    social_twitter = fields.Char(related=False)
    social_facebook = fields.Char(elated=False)
    social_github = fields.Char(related=False)
    social_linkedin = fields.Char(related=False)
    social_youtube = fields.Char(related=False)
    social_googleplus = fields.Char(related=False)
    social_instagram = fields.Char(related=False)
    email = fields.Char(string='Website Email', related=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_id = fields.Many2one('website', string="website", default=_default_website, required=True)
    social_instagram = fields.Char(string='Website Email', related='website_id.social_instagram')



