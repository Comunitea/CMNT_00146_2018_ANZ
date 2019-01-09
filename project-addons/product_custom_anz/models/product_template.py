# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    product_color = fields.Many2one('product.attribute.value', string="Color",
                                    domain="[('is_color','=', True)]")
    boot_type = fields.Many2one(
        'product.attribute.value',
        string="Tipo de bota", domain="[('is_tboot','=', True)]")
    replication = fields.Boolean('Replication')
    variant_suffix = fields.Char(
        'Variant suffix', compute="_get_variant_suffix", store=True)
    pvp = fields.Float('PVP', digits=(16, 2))
    ref_template = fields.Char('Ref Template')
    importation_name = fields.Char('Importation name')

    @api.multi
    @api.depends('attribute_line_ids')
    def _get_variant_suffix(self):
        for template in self:
            names = template.attribute_line_ids.mapped('value_ids').\
                mapped('name')
            if names:
                template.variant_suffix = \
                    " ({})".format(", ".join([v for v in names]))
            else:
                template.variant_suffix = ''

    @api.model
    def _search(self, args, offset=0, limit=None, order=None,
                count=False, access_rights_uid=None):
        partner = self.env['res.partner'].get_partner_by_context()
        if partner and not partner.affiliate:
            args = partner.add_args_to_product_search(args)
        return super(ProductTemplate, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid)

    @api.multi
    def unlink(self):
        """
        Delete the xml_id of related variants
        """
        variant_ids = self.mapped('product_variant_ids').ids
        super().unlink()
        if variant_ids:
            Data = self.env['ir.model.data'].sudo().with_context({})
            data = Data.search([
                ('model', '=', 'product.product'),
                ('res_id', 'in', variant_ids)])
            if data:
                data.unlink()


class ProductProduct(models.Model):

    _inherit = 'product.product'
    oldname = fields.Char()

    @api.model
    def _search(self, args, offset=0, limit=None, order=None,
                count=False, access_rights_uid=None):
        partner = self.env['res.partner'].get_partner_by_context()
        if partner and not partner.affiliate:
            args = partner.add_args_to_product_search(args)
        return super(ProductProduct, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid)
