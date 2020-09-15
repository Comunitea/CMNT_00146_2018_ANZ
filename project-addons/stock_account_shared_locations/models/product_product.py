# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields



class Product(models.Model):
    _inherit = "product.product"

    def _get_domain_locations(self):
        # return super()._get_domain_locations()
        '''
        Parses the context and returns a list of location_ids based on it.
        It will return all stock locations when no parameters are given
        Possible parameters are shop, warehouse, location, force_company, compute_child
        '''
        if self.env.context.get('company_owned', False):
            return (
                [('location_id.company_id', '=', False), ('location_id.usage', '=', 'internal')],
                [('location_id.usage', '!=', 'internal'), ('location_dest_id.usage', '=', 'internal')],
                [('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '!=', 'internal'),
            ])
        return super()._get_domain_locations()
