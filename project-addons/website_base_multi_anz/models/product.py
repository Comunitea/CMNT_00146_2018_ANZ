# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductPublicCategoryTag(models.Model):
    _name = "product.public.category.tag"
    _description = "Website Product Category Related Tag"
    _order = "name"

    name = fields.Char(translate=True)


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    public_categ_tag_ids = fields.Many2many('product.public.category.tag',
                                            'public_categ_tag_rel',
                                            'category_id',
                                            'tag_id',
                                            string='Related Tags',
                                            help="Find Website Categories in Search Box by Related Tags")
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    inventory_availability = fields.Selection(selection_add=[
        ('always_virtual', _('Show future and current inventory on website and prevent sales if not enough stock')),
        ('threshold_virtual',
         _('Show future and current inventory below a threshold and prevent sales if not enough stock'))
    ])

    @api.multi
    def act_stock_published(self, domain=[]):
        # campos que mostraran siempre independiente del inventario
        tsw = self.env['template.stock.web']
        swp_fields = ['always', 'always_virtual', 'threshold_virtual']
        ctx = self._context.copy()

        template_ids = self.env['product.template'].search([('website_published', '=', True)])
        for template in template_ids:
            for website in template.website_ids:
                inventory_availability = template.inventory_availability or website.inventory_availability
                if inventory_availability in swp_fields:
                    stock_website_published = True
                else:
                    ctx.update(warehouse_id=website.warehouse_id.id)
                    stock_website_published = template.with_context().qty_available > 0

                vals = {'product_id': template.id, 'website_id': website.id,
                        'stock_website_published': stock_website_published}
                domain = [('product_id', '=', template.id), ('website', '=', website.id)]
                tsw_id = tsw.search(domain)
                if tsw_id:
                    tsw_id.stock_website_published = stock_website_published
                else:
                    self.env['template.stock.web'].create(vals)


class TemplateStockWeb(models.Model):
    _name = "template.stock.web"

    product_id = fields.Many2one('product.template')
    website_id = fields.Many2one('website', 'Website')
    stock_website_published = fields.Boolean('Publicado sin stock')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_web_max_qty(self):
        """
        Determina la cantidad maxima disponible del producto a partir de la cual se va a mostrar el stock del
        producto en la web. Esto se realiza en función de las diferentes opciones de inventory_availability.

        :return: max_qty
        """
        max_qty = -1
        if self.inventory_availability in ['always', 'threshold']:
            max_qty = max(0, self.qty_available - self.sudo().outgoing_qty)
        elif self.inventory_availability in ['always_virtual', 'threshold_virtual']:
            max_qty = max(0, self.virtual_available)

        if self.inventory_availability in ['threshold', 'threshold_virtual'] \
                and self.product_tmpl_id.available_threshold > 0:
            max_qty = max(0, max_qty - self.product_tmpl_id.available_threshold)
        return max_qty

