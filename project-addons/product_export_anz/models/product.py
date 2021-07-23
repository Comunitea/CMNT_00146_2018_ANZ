# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api, _



class ProductTemplate(models.Model):
    _inherit = 'product.template'


    @api.multi
    @api.depends('public_categ_ids')
    def _get_export_categ_str(self):
        rest = len(self)
        for template in self:
            
            rest -= 1
            
            vals = {}
            cont = 0
            for categ in template.public_categ_ids:
                if cont <10:
                    field_name = 'categ_str%d'%cont
                    cont +=1
                    vals[field_name] = categ.display_name

            while cont<10:
                field_name = 'categ_str%d'%cont
                vals[field_name] = ''
                cont +=1
            print ("{}: {}: {} >>>>>> {}".format(template.name, template.public_categ_ids.mapped('display_name'), rest, vals))
            template.write(vals)


    categ_str1 = fields.Char("Categ Str 1", compute = _get_export_categ_str, store=True)
    categ_str2 = fields.Char("Categ Str 2", compute = _get_export_categ_str, store=True)
    categ_str3 = fields.Char("Categ Str 3", compute = _get_export_categ_str, store=True)
    categ_str4 = fields.Char("Categ Str 4", compute = _get_export_categ_str, store=True)
    categ_str5 = fields.Char("Categ Str 5", compute = _get_export_categ_str, store=True)
    categ_str6 = fields.Char("Categ Str 6", compute = _get_export_categ_str, store=True)
    categ_str7 = fields.Char("Categ Str 7", compute = _get_export_categ_str, store=True)
    categ_str8 = fields.Char("Categ Str 8", compute = _get_export_categ_str, store=True)
    categ_str9 = fields.Char("Categ Str 9", compute = _get_export_categ_str, store=True)
    categ_str0 = fields.Char("Categ Str 0", compute = _get_export_categ_str, store=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('categ_id', 'attribute_value_ids' , 'attribute_value_ids.attribute_id', 'attribute_value_ids.name')
    def _get_export_str(self):
        # Modo test solo los primaros 100
        
        for product in self:
            
            export_str_categ = product.categ_id.display_name
            attrib_ids = product.attribute_value_ids.filtered(lambda x: x.active)
            names = attrib_ids.filtered(lambda x: not x.attribute_id.main).sorted(lambda x:x.attribute_id.is_color).mapped('name')
            export_str_attrib_str = "{}".format(", ".join([v for v in names]))
            attrib_talla = attrib_ids.filtered(lambda x: x.attribute_id.main)
            if attrib_talla:
                export_str_atrib_talla = attrib_talla[0].attribute_id.name
                export_str_value_talla = attrib_talla[0].name
            export_str_color= attrib_ids.filtered(lambda x: x.attribute_id.is_color).name
            export_str_image_url = "https://skipping.es/web/image/product.template/{}/image".format(product.product_tmpl_id.id)
            product.export_str_categ = export_str_categ
            product.export_str_image_url = export_str_image_url
            product.export_str_atrib_talla = export_str_atrib_talla
            product.export_str_color = export_str_color
            product.export_str_value_talla = export_str_value_talla
            product.export_str_attrib_str = export_str_attrib_str
            
    
    export_str_categ = fields.Char("Categoría (str)", compute=_get_export_str, store=True)
    export_str_image_url = fields.Char("Image URL (str)", compute=_get_export_str, store=True)
    export_str_atrib_talla = fields.Char("Tipo talla (str)", compute=_get_export_str, store=True)
    export_str_color = fields.Char("Color (str)", compute=_get_export_str, store=True)
    export_str_value_talla = fields.Char("Talla", compute=_get_export_str, store=True)
    export_str_attrib_str = fields.Char("Atributos", compute=_get_export_str, store=True)
    export_str_meta_keywords = fields.Char(related="product_meta_keywords", string="Meta Keywords (str)")

    
    """
    export_str_categ = fields.Char("Categoría (str)")
    export_str_image_url = fields.Char("Image URL (str)")
    export_str_atrib_talla = fields.Char("Tipo talla (str)")
    export_str_color = fields.Char("Color (str)")
    export_str_value_talla = fields.Char("Talla")
    export_str_attrib_str = fields.Char("Atributos")
    export_str_meta_keywords = fields.Char(related="product_meta_keywords", string="Meta Keywords (str)")
    """