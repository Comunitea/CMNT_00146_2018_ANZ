# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'


    @api.model
    def _get_in_base_domain(self, company_id=False):

        """
        Originalmente se encuntran los movimientos de entrada por compañia de las ubiicaciones, lo cambiosmos por el tipo de utilización de la compañia
        :param company_id:
        :return:
        """
        domain = [
            ('state', '=', 'done'),
            ('location_id.usage', '!=', 'internal'),
            ('location_dest_id.usage', '=', 'internal')
        ]
        return domain

    @api.model
    def _get_all_base_domain(self, company_id=False):
        """
        Heredo toda la funcion para cambiar lo que devuelvo para hacer el filtro por tipo = internal en vez de por compañia.
        y saco la comañia paa filtrar por movimientos.
        :param company_id:
        :return:
        """

        domain = [
            ('state', '=', 'done'),
            '|',
                '&',
                    ('location_id.usage', '!=', 'internal'),
                    ('location_dest_id.usage', '=', 'internal'),
                '&',
                    ('location_id.usage', '=', 'internal'),
                    ('location_dest_id.usage', '!=', 'internal')
        ]
        return domain
