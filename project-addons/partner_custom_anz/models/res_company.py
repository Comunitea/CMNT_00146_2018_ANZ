# © 2016 Comunitea - Kiko Sánchez<kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.exceptions import UserError,ValidationError



class ResUser(models.Model):

    _inherit = 'res.company'

    stock_global = fields.Boolean("Show stock global?")