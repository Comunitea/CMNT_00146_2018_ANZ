# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for product in env['product.template'].search([('ref_change_code', '=', False)]):
            product.ref_change_code = product._default_ref_change_code()
