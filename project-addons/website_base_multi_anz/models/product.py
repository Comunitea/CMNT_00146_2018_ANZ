# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


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
    visibility_stock_web = fields.One2many('template.stock.web', 'product_id')

    def delete_tsw(self, website):
        """
        Disassociate product with his website setting stock_website_published to false.
        """
        domain = [('product_id', '=', self.id), ('website_id', '=', website.id)]
        tsw_id = self.env['template.stock.web'].search(domain)
        if len(tsw_id) > 1:
            tsw_id.unlink()
            vals = {'product_id': self.id, 'website_id': website.id,
                    'stock_website_published': False}
            self.env['template.stock.web'].create(vals)
        elif tsw_id:
            tsw_id.stock_website_published = False


    def create_tsw(self, website):
        """
        Associate product with his website setting stock_website_published to true if max_qty > 0.
        """
        ctx = self._context.copy()
        swp_fields = ['always_virtual', 'threshold_virtual']
        inventory_availability = self.inventory_availability or website.inventory_availability

        if inventory_availability in swp_fields:
            stock_website_published = True
        else:
            ctx.update(warehouse=website.warehouse.id)
            stock_website_published = self.with_context(ctx).get_web_max_qty() > 0

        vals = {'product_id': self.id, 'website_id': website.id,
                'stock_website_published': stock_website_published}
        domain = [('product_id', '=', self.id), ('website_id', '=', website.id)]
        tsw_id = self.env['template.stock.web'].search(domain)
        if len(tsw_id) > 1:
            tsw_id.unlink()
            self.env['template.stock.web'].create(vals)
        elif tsw_id:
            tsw_id.stock_website_published = stock_website_published
        else:
            self.env['template.stock.web'].create(vals)

    def get_web_max_qty(self):
        """
        Determina la cantidad maxima disponible del producto a partir de la cual se va a mostrar el stock del
        producto en la web. Esto se realiza en función de las diferentes opciones de inventory_availability.
        Se llama desde multi_update_cart cuando se añaden productos desde el grid de variantes en la web.

        :return: max_qty
        """
        # Old way
        # max_qty = -1
        # if self.inventory_availability in ['always', 'threshold']:
        #     max_qty = max(0, self.qty_available - self.sudo().outgoing_qty)
        #
        # if self.inventory_availability in ['threshold'] and self.available_threshold > 0:
        #     max_qty = max(0, max_qty - self.available_threshold)
        # return max_qty

        # New way. Same way as act_stock_published because is more complete
        max_qty = -1
        if self.inventory_availability in ['always', 'threshold']:
            max_qty = max(0, self.qty_available - self.sudo().outgoing_qty)
        elif self.inventory_availability in ['always_virtual', 'threshold_virtual']:
            max_qty = max(0, self.virtual_available)

        if self.inventory_availability in ['threshold', 'threshold_virtual'] and self.available_threshold > 0:
            max_qty = max(0, max_qty - self.available_threshold)
        return max_qty

    @api.model
    def act_stock_published(self):
        """
        Update product visibility in websites by stock.
        If product have assigned one or more website the visibility will be for them.
        If product have assigned none website the visibility will be for all websites.
        Only products with stock > 0 are visible except if in inventory_availability check for future stock.
        You can run this by programmer action in backend.
        You can check visibility for every website on product in backend menu.
        """
        template_ids = self.env['product.template'].search([('website_published', '=', True)])
        cont = 0
        tot = len(template_ids)
        template_stock_web_error_domain = [('website_id', '=', False)]
        self.env['template.stock.web'].search(template_stock_web_error_domain).unlink()

        for template in template_ids:
            cont += 1
            _logger.info('{}: {} de {}: {}'.format('Update Website Visibility by Stock', cont, tot, template.name))
            template_websites = template.website_ids
            all_websites = self.env['website'].search([])
            for website in all_websites:
                if website in template_websites or len(template_websites) == 0:
                    template.create_tsw(website)
                else:
                    template.delete_tsw(website)


class TemplateStockWeb(models.Model):
    _name = "template.stock.web"

    product_id = fields.Many2one('product.template')
    website_id = fields.Many2one('website', string='Website')
    stock_website_published = fields.Boolean(string='Stock Visible')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_web_max_qty(self):
        """
        Determina la cantidad maxima disponible del producto a partir de la cual se va a mostrar el stock del
        producto en la web. Esto se realiza en función de las diferentes opciones de inventory_availability.
        Se llama desde act_stock_published al ejecutarse la acción programada
        para no publicar articulos sin stock en la web.

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

    def delete_all_variable_images(self):
        variables_with_images = self.search([('image_variant', '!=', False)])
        variables_with_images.update({
            'image_variant': False,
        })

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        """
        Workaround para que funcione el carrito con las cantidades correctas en los productos con ubicaciones sin compañia.
        Cuando se establezca la compañía a las ubicaciones hay que borrar este método.
        """
        # TODO: Borrar cuando se establezca la compañía a las ubicaciones hay que borrar este método
        ctx = self._context.copy()
        if 'from_website' in ctx:
            # ctx.pop('from_website')
            ctx.pop('force_company')
        return super(ProductProduct, self.with_context(ctx))._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date, to_date)
