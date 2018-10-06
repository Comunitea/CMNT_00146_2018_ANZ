# Copyright 2004 Omar Castiñeira Saavedra <omar@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "IGIC (Impuesto General Indirecto Canario)",
    "version": "11.0.1.0.0",
    "author": "David Diz Martínez <daviddiz@gmail.com>,"
              "Atlantux Consultores - Enrique Zanardi,"
              "Comnunitea,"
              "Odoo Community Association (OCA)",
    "website": "https://comunitea.com",
    "category": "Localization/Europe",
    "depends": [
        "l10n_es",
    ],
    "license": "AGPL-3",
    "data": [
        "data/account_chart_template_igic.xml",
        "data/account_account_igic.xml",
        "data/taxes_igic.xml",
        "data/fiscal_positions_igic.xml",
    ],
    'installable': True
}
