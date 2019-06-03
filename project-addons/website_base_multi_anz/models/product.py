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

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    inventory_availability = fields.Selection(selection_add=[
        ('always_virtual', _('Show future and current inventory on website and prevent sales if not enough stock')),
        ('threshold_virtual',
         _('Show future and current inventory below a threshold and prevent sales if not enough stock'))
    ])

    stock_website_published = fields.Boolean('Publicado sin stock')


    @api.multi
    def act_stock_published(self, domain=[]):

        if domain:
            domain += [('type', '=', 'product'), ('website_published', '=', True)]
        templates = self.filtered(lambda x: x.type == 'product' and x.website_published == 'True') or self.search(domain)
        for tmpl in templates:
            tmpl.stock_website_published = tmpl.website_published and tmpl.virtual_available > 0

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        self.mapped('product_id').mapped('product_tmpl_id').act_stock_published()
