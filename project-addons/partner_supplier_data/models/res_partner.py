# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.exceptions import UserError,ValidationError

class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    def get_supplier_customer_count(self, customer_domain = []):
        for partner in self:
            partner.customer_data_count = partner.customer and self.env['partner.supplier.data'].search_count(customer_domain + [('partner_id', '=', partner.id)]) or 0
            partner.supplier_data_count = partner.supplier and self.env['partner.supplier.data'].search_count(customer_domain + [('supplier_id', '=', partner.id)]) or 0

    partner_supplier_data_ids = fields.One2many('partner.supplier.data', 'supplier_id', string="Partner supplier data", help ="Customers for this supplier")
    partner_customer_data_ids = fields.One2many('partner.supplier.data', 'partner_id', string="Partner supplier data", help="Supplier data for this customer")
    supplier_data_count = fields.Integer('Count', compute='get_supplier_customer_count')
    customer_data_count = fields.Integer('Count', compute='get_supplier_customer_count')
    import_from = fields.Char('Import from')

    @api.multi
    def get_supplier_partner(self, supplier_code=False, supplier_id=False, brand_id=False):
        domain = []
        if supplier_code:
            domain += [('supplier_code', '=', supplier_code)]
        if supplier_id:
            domain += [('supplier_id', '=', supplier_id)]
        #if brand_id:
        #    domain += [('brand_id', '=', brand_id)]
        partner_id = self.env['partner.supplier.data'].search(domain)
        if len(partner_id)==1:
            return partner_id.partner_id
        return False


    @api.multi
    def act_location_dates_from_zip(self):
        self._compute_commercial_partner()
        for partner in self:
            better_zip = self.env['res.batter.zip'].search([('name', '=', partner.zip)], limit=1)
            if better_zip:
                partner.write({'zip_id': better_zip.id,
                               'state_id': better_zip.state_id.id,
                               'country_id': better_zip.country_id.id,
                               'city': better_zip.city})

    @api.multi
    def _compute_commercial_partner(self):
        no_comercial = self.filtered(lambda x:x.is_company==False and not x.parent_id)
        no_comercial.comercial_partner_id = False
        return super(ResPartner, self-no_comercial)._compute_commercial_partner()
