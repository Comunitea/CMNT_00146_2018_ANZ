# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.depends('product_variant_ids', 'product_variant_ids.standard_price')
    def _template_standard_price(self):
        ##SOBRE ESCRIBO TODA LA FUNCION PARA NO REHACER EL CALCULO

        for template in self:
            template.template_standard_price = template.product_variant_ids and template.product_variant_ids[0].standard_price or 0.00


    product_color = fields.Many2one('product.attribute.value', string="Color",
                                    domain="[('is_color','=', True)]")
    boot_type = fields.Many2one(
        'product.attribute.value',
        string="Tipo de bota", domain="[('is_tboot','=', True)]")
    replication = fields.Boolean('Replication')
    attribute_id = fields.Many2one('product.attribute')
    variant_suffix = fields.Char('Variant suffix')
    pvp = fields.Float('PVP', digits=(16, 2))
    ref_template = fields.Char('Ref Template')
    importation_name = fields.Char('Importation name')
    template_standard_price = fields.Float('Precio de coste', compute=_template_standard_price,
        digits=dp.get_precision('Product Price'))
    numero_de_variantes = fields.Integer('Numero de variantes')


    @api.multi
    @api.onchange("attribute_line_ids")
    def _get_variant_suffix(self):
        total = len(self)
        idx=0

        for template in self:
            idx+=1
            template.attribute_id = template.attribute_line_ids and template.attribute_line_ids[0].attribute_id or False
            template.numero_de_variantes = template.product_variant_count
            names = template.attribute_line_ids.mapped('value_ids').\
                mapped('name')

            if names:
                template.variant_suffix = \
                    " ({})".format(", ".join([v for v in names]))
            else:
                if template.product_variant_count == 1:
                    template.variant_suffix = 'Sin variantes'
                else:
                    template.variant_suffix = 'Sin valores en variantes'
            print ("{} de {}  -> {}:  {}".format(idx, total, template.name, template.variant_suffix ))

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

    @api.multi
    def _get_attribute_id(self):
        for product in self:
            product.attribute_id = product.product_tmpl_id.attribute_line_ids and product.product_tmpl_id.attribute_line_ids[0].attribute_id or False

    oldname = fields.Char()
    #attribute_id = fields.Many2one('product.attribute', compute="_get_attribute_id")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None,
                count=False, access_rights_uid=None):
        partner = self.env['res.partner'].get_partner_by_context()
        if partner and not partner.affiliate:
            args = partner.add_args_to_product_search(args)
        return super(ProductProduct, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid)
