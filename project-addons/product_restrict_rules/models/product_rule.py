# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ProductRule(models.Model):

    _name = "product.rule"

    name = fields.Char('Name', required=True)
