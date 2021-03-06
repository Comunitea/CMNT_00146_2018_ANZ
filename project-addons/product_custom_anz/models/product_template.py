# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, except_orm, UserError
import itertools
import psycopg2


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.depends('product_variant_ids', 'product_variant_ids.standard_price')
    def _template_standard_price(self):
        for template in self:
            template.template_standard_price = template.product_variant_ids and template.product_variant_ids[0].standard_price or 0.00


    #list_price = fields.Float(company_dependent=True)
    product_color = fields.Many2one('product.attribute.value', string="Color",
                                    domain="[('is_color','=', True)]")
    boot_type = fields.Many2one(
        'product.attribute.value',
        string="Tipo de bota", domain="[('is_tboot','=', True)]")
    replication = fields.Boolean('Replication')
    attribute_id = fields.Many2one('product.attribute')
    variant_suffix = fields.Char('Variant suffix')
    pvp = fields.Float('PVP', digits=(16, 2))

    # TODO Mostrar estos campos al editar
    ref_template = fields.Char('Referencia de plantilla')
    ref_template_color = fields.Char('Color de la referencia de plantilla')
    ref_template_name = fields.Char(compute='_compute_ref_template_name',
                               search='_search_ref_template_name')

    @api.depends('ref_template', 'ref_template_color')
    def _compute_ref_template_name(self):
        for record in self:
            ref_template_name = ''
            if record.ref_template:
                ref_template_name = record.ref_template
                if record.ref_template_color:
                    ref_template_name += " " + record.ref_template_color
            record.ref_template_name = ref_template_name                

    def _search_ref_template_name(self,operator,value):
        if operator.find('like') >= 0:
            value = str(value)
            comparator = " concat(ref_template,'[ -]',ref_template_color) "
            if operator.find('ilike') >= 0:
                comparator = comparator.lower()
                value = value.lower()
            if operator.find('=') >= 0:
                operator = operator.replace('=','')
            else:
                value = '%' + value + '%'
            self.env.cr.execute("SELECT id FROM product_template WHERE "+comparator+operator+" '"+value+"';")
        # else:
        #     ValidationError(_('The field risk_exception is not searchable '
        #                     'with the operator {} and value {}'.format(operator,value)))
        return [('id','in',[i[0] for i in self.env.cr.fetchall()])]

    importation_name = fields.Char('Importation name')
    numero_de_variantes = fields.Integer('Numero de variantes')

    @api.multi
    @api.onchange("attribute_line_ids")
    def _get_variant_suffix(self):
        """ """
        total = len(self)
        idx = 0
        for template in self:
            idx += 1
            template.attribute_id = template.attribute_line_ids and template.attribute_line_ids.filtered('main').attribute_id or False
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
            #print("{} de {}  -> {}: Variantes: {} Sufijo: {}".format(idx, total, template.name, template.numero_de_variantes, template.variant_suffix))

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
        """
        SOBREESCRITA PARA QUE SOLO CREE VARIANTES CON LOS ATRIBUTOS MAIN
        NO QUEREMOS QUE AL CAMBIAR UN ATRIBUTO FEATURE NOS DESACTIVE Y CREE
        NUEVAS VARIANTES
        (todos los filtered por .main antes eran por .create_variant)
        SE AÑADE NUEVO CASO AL FINAL DE LA FUNCIÓN PARA BORRAR LOS ATRIBUTOS
        QUE SON FEATURE Y VOLVERLOS A ENLAZAR (ACTUALIZANDOLOS ASÍ)
        El resto de la función es la original del módulo de product.
        No hay herencias instaladas (módulo product_variant_configurator)
        """
        if self._context.get('no_create_variants', False):
            return True
        Product = self.env["product.product"]
        AttributeValues = self.env['product.attribute.value']
        for tmpl_id in self.with_context(active_test=False):
            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            variant_alone = tmpl_id.attribute_line_ids.filtered(lambda line: line.attribute_id.main and len(line.value_ids) == 1).mapped('value_ids')
            for value_id in variant_alone:
                updated_products = tmpl_id.product_variant_ids.filtered(lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
                updated_products.write({'attribute_value_ids': [(4, value_id.id)]})

            # iterator of n-uple of product.attribute.value *ids*
            variant_matrix = [
                AttributeValues.browse(value_ids)
                for value_ids in itertools.product(*(line.value_ids.ids for line in tmpl_id.attribute_line_ids if line.value_ids[:1].attribute_id.main))
            ]

            # get the value (id) sets of existing variants
            existing_variants = {frozenset(variant.attribute_value_ids.filtered(lambda r: r.attribute_id.main).ids) for variant in tmpl_id.product_variant_ids}
            # -> for each value set, create a recordset of values to create a
            #    variant for if the value set isn't already a variant
            to_create_variants = [
                value_ids
                for value_ids in variant_matrix
                if set(value_ids.ids) not in existing_variants
            ]

            # check product
            variants_to_activate = self.env['product.product']
            variants_to_unlink = self.env['product.product']
            for product_id in tmpl_id.product_variant_ids:
                if not product_id.active and product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.main) in variant_matrix:
                    variants_to_activate |= product_id
                elif product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.main) not in variant_matrix:
                    variants_to_unlink |= product_id
            if variants_to_activate:
                variants_to_activate.write({'active': True})

            # create new product
            for variant_ids in to_create_variants:
                new_variant = Product.create({
                    'product_tmpl_id': tmpl_id.id,
                    'attribute_value_ids': [(6, 0, variant_ids.ids)]
                })

            # unlink or inactive product
            for variant in variants_to_unlink:
                try:
                    with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                        variant.unlink()
                # We catch all kind of exception to be sure that the operation doesn't fail.
                except (psycopg2.Error, except_orm):
                    variant.write({'active': False})
                    pass

            # NUEVO CASO, ACTUALIZAR LOS VALORES DE ATRIBUTO QUE SON FEATURE
            # BORRAR
            old_feature_values = tmpl_id.product_variant_ids.mapped('attribute_value_ids').filtered(lambda val: val.attribute_id.feature)
            if old_feature_values:
                # El unlink salta un error que no se puede saltar heredando, uso sql
                # old_feature_values.unlink()
                self._cr.execute('DELETE FROM product_attribute_value_product_product_rel WHERE product_attribute_value_id IN %s and product_product_id IN %s' % ( str(tuple(old_feature_values.ids)).replace(',)', ')'), str(tuple(tmpl_id.product_variant_ids.ids)).replace(',)', ')')))

            # VOLVER A ENLAZAR
            new_features = tmpl_id.attribute_line_ids.filtered(lambda line: line.attribute_id.feature and len(line.value_ids) == 1).mapped('value_ids')
            for value_id in new_features:
                tmpl_id.product_variant_ids.write({'attribute_value_ids': [(4, value_id.id)]})
        return True

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
                    tmpl.attribute_line_ids.filtered('main').with_context(ctx).write({'value_ids': [(4, val_id.id)]})
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

    @api.multi
    def set_brand_attribute(self, brand):
        self.ensure_one()
        att_brand = self.env['product.attribute'].search(
            [('name', '=', 'MARCA')])
        if not att_brand:
            raise ValidationError(_('Attribute Brand not founded'))

        domain = [
                ('attribute_id', '=', att_brand.id),
                ('name', '=', brand.name),
            ]
        value = self.env['product.attribute.value'].search(domain,
                                                            limit=1)
        if not value:
            raise UserError(
                _('Not value found for equivalent to brand %s') % brand.name)

        brand_att_line = self.attribute_line_ids.filtered(
            lambda l: l.attribute_id.id == att_brand.id
        )

        if brand_att_line:
            brand_att_line = brand_att_line[0]
            brand_att_line.write({'value_ids': [(6, 0, [value.id])]})
        else:
            vals = {
                'product_tmpl_id': self.id,
                'attribute_id': att_brand.id,
                'value_ids': [(6, 0, [value.id])],
            }
            att_lst_vals = [(0, 0, vals)]
            self.write({'attribute_line_ids': att_lst_vals})

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get('product_brand_id'):
            brand = self.env['product.brand'].browse(vals['product_brand_id'])
            res.set_brand_attribute(brand)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('product_brand_id'):
            brand = self.env['product.brand'].browse(vals['product_brand_id'])
            for tmp in self:
                if not tmp.product_brand_id or (tmp.product_brand_id and
                                                tmp.product_brand_id.id !=
                                                brand.id):
                    tmp.set_brand_attribute(brand)
        res = super().write(vals)
        return res


class ProductProduct(models.Model):

    _inherit = 'product.product'

    #standard_price = fields.Float(company_dependent=True)

    @api.multi
    def _get_attribute_id(self):
        for product in self:
            product.attribute_id = product.product_tmpl_id.attribute_line_ids and product.product_tmpl_id.attribute_line_ids.filtered('main').attribute_id or False

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
        product_ids = self.env['product.product'].search([('barcode','!=','')])
        len_p = len(product_ids)
        print ("Actualizando {} productos".format(len_p))
        i=0
        delete_xml_id(model)
        for p in product_ids:
            i+=1
            print("Van {} de {}".format(i, len_p))
            create_xml_id(p.barcode, p.id, model)
