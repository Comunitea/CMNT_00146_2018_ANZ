# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    type = fields.Selection(default='product')

    @api.depends('product_variant_ids', 'product_variant_ids.standard_price')
    def _template_standard_price(self):
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
    fields.Many2one('product.attribute')
    numero_de_variantes = fields.Integer('Numero de variantes')
    sql_constraints = [
        ("unique_template_ref", "UNIQUE(ref_template)",
         "Cannot have more than one template with same code.")
    ]

    @api.multi
    @api.onchange("attribute_line_ids")
    def _get_variant_suffix(self):

        total = len(self)
        idx = 0
        for template in self:
            idx += 1
            template.attribute_id = template.attribute_line_ids and template.attribute_line_ids[0].attribute_id or False
            template.numero_de_variantes = template.product_variant_count
            names = template.attribute_line_ids.mapped('value_ids').mapped('name')
            if names:
                template.variant_suffix = \
                    " ({})".format(", ".join([v for v in names]))
            else:
                if template.product_variant_count == 1:
                    template.variant_suffix = 'Sin variantes'
                else:
                    template.variant_suffix = 'Sin valores en variantes'
            print("{} de {}  -> {}: Variantes: {} Sufijo: {}".format(idx, total, template.name, template.numero_de_variantes, template.variant_suffix))

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

    @api.multi
    def create_variant_ids(self):
        if self._context.get('no_create_variants', False):
            return True
        return super(ProductTemplate, self).create_variant_ids()

    @api.multi
    def fix_variant_attributes(self):
        ctx = self._context.copy()
        ctx.update(no_create_variants=True)
        tmpl_ids = self.filtered(lambda x: x.attribute_id)
        for tmpl in tmpl_ids:
            change_template = False
            values = tmpl.attribute_id.value_ids
            variant_ids = tmpl.product_variant_ids.filtered(lambda x: not x.attribute_value_ids and x.oldname)
            print ("\n\nBusco \n{} en \n{}".format(values.mapped('name'), variant_ids.mapped('oldname')))
            for variant in variant_ids.sorted(key=lambda l: len(l.oldname), reverse=True):
                print ("\n -------------> {}".format(variant.oldname))
                val_id = False
                if not variant.force_attribute_value:
                    for val in values.sorted(key=lambda l: len(l.name), reverse=True):
                        print ('{} -> {}'.format(val.name, variant.oldname))
                        if val.name in variant.oldname or (val.name_normalizado and val.name_normalizado in variant.oldname_normalizado):
                            print('-------------> ---> Encuentro {} la variante {}'.format(variant.oldname, val.name))
                            if val_id:
                                val_id = False
                                variant.need_fix = True
                                print ('-------------> XXX> Duplicado {} -> {}'.format(val.name, variant.oldname))
                            else:
                                val_id = val
                else:
                    val_id = variant.force_attribute_value
                if val_id:
                    variant.need_fix = False
                    change_template = True
                    print('-------------> ---> ---> Escribo en {} la variante {}'.format(variant.oldname, val_id.name))
                    variant.write({'attribute_value_ids': [(6,0,[val_id.id])]})
                    tmpl.attribute_line_ids[0].with_context(ctx).write({'value_ids': [(4, val_id.id)]})
                else:
                    print('-------------> ---> La variante {} no tiene talla'.format(variant.oldname))
                #else:
                #    variant.write({'attribute_value_ids': [(5)]})
            if change_template:
                tmpl._get_variant_suffix()

    @api.multi
    def refresh_xml_id_product_template(self):
        def delete_xml_id(model):
            sql = "delete from ir_model_data where model = '{}'".format(model)
            self._cr.execute(sql)

        def create_xml_id(xml_id, res_id, model):
            virual_module_name = 'PT' if model == 'product.template' else 'PP'
            vals = {
                'module': virual_module_name,
                'name': xml_id.lower(),
                'res_id': res_id,
                'model': model
            }
            self.env['ir.model.data'].create(vals)


        model = 'product.template'
        product_ids = self.env[model].search(['|', ('ref_template','=', ''), ('default_code', '!=', '')])
        len_p = len(product_ids)
        print("Actualizando {} registros".format(len_p))
        i = 0
        delete_xml_id(model)
        for p in product_ids:
            i += 1
            print("Van {} de {}".format(i, len_p))
            d_c = p.default_code or p.ref_template
            create_xml_id(d_c, p.id, model)


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.multi
    def _get_attribute_id(self):
        for product in self:
            product.attribute_id = product.product_tmpl_id.attribute_line_ids and product.product_tmpl_id.attribute_line_ids[0].attribute_id or False

    oldname = fields.Char()
    oldname_normalizado = fields.Char()
    tmpl_attribute_id = fields.Many2one(related="product_tmpl_id.attribute_id")
    need_fix = fields.Boolean(default=False)
    force_attribute_value = fields.Many2one('product.attribute.value', string="Forzar esta talla")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None,
                count=False, access_rights_uid=None):
        partner = self.env['res.partner'].get_partner_by_context()
        if partner and not partner.affiliate:
            args = partner.add_args_to_product_search(args)
        return super(ProductProduct, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid)


    @api.multi
    def refresh_xml_id_product_product(self):
        def delete_xml_id(model):
            sql = "delete from ir_model_data where model = '{}'".format(model)
            self._cr.execute(sql)

        def create_xml_id(xml_id, res_id, model):
            virual_module_name = 'PT' if model == 'product.template' else 'PP'
            vals = {
                'module': virual_module_name,
                'name': xml_id.lower(),
                'res_id': res_id,
                'model': model
            }
            self.env['ir.model.data'].create(vals)



        model = 'product.product'
        product_ids = self.env['product.product'].search([('default_code','!=','')])
        len_p = len(product_ids)
        print ("Actualizando {} productos".format(len_p))
        i=0
        delete_xml_id(model)
        for p in product_ids:
            i+=1
            print("Van {} de {}".format(i, len_p))
            create_xml_id(p.default_code, p.id, model)

