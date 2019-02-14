# © 2016 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.exceptions import UserError,ValidationError



class SupplierClass(models.Model):

    _name = 'supplier.customer.ranking'
    _order = 'sequence, supplier_id, code'

    sequence = fields.Integer('Sequence')
    supplier_id = fields.Many2one('res.partner', 'Proveedor', domain="[('supplier', '=', True)]", required='1')
    name = fields.Char("Nombre", required="1")
    code = fields.Char('Código externo')
    description = fields.Char('Descripción')

class ResPartnerSupplierData(models.Model):
    _name = 'partner.supplier.data'

    @api.multi
    def get_default_ranking(self, supplier_id = False):
        if not supplier_id:
            supplier_id = self.supplier_id.id
        if not supplier_id:
            return False
        return self.env['supplier.customer.ranking'].search([('supplier_id', '=', supplier_id)], limit=1)


    partner_id = fields.Many2one(related='customer_supplier_id.commercial_partner_id')
    name = fields.Char(related="customer_supplier_id.name", string="Nombre")
    customer_supplier_id = fields.Many2one('res.partner', "Cliente externo",
                                          domain="[('type', '=', 'other'), ('supplier', '=', False)]",
                                          help="Type=Other, must be child of partner_id")
    #brand_id = fields.Many2one('product.brand', 'Brand')
    supplier_id = fields.Many2one('res.partner', 'Proveedor', domain="[('supplier', '=', True)]")
    supplier_code = fields.Char("Código externo")
    supplier_str = fields.Char("Nombre en factura")
    supplier_customer_ranking_id = fields.Many2one('supplier.customer.ranking', string="Clasificación")
    active = fields.Boolean('Active', default=True)


    _sql_constraints = [
        ('name_supplier_code', 'unique(supplier_code, supplier_id)',
         _('Supplier code must be unique')),
    ]
    @api.onchange('supplier_id')
    def onchange_supplier_id(self):
        if self.supplier_id:
            self.supplier_customer_ranking_id = self.get_default_ranking(self.supplier_id.id)
        else:
            self.supplier_customer_ranking_id = False

    @api.multi
    def unlink(self):
        partner_to_unlink = self.mapped('customer_supplier_id')
        res = super().unlink()
        partner_to_unlink.unlink()
        return res

    @api.model
    def create(self, vals):
        if not vals.get ('supplier_customer_ranking_id', False):
            vals['supplier_customer_ranking_id'] = self.get_default_ranking(vals['supplier']).id
        return super(ResPartnerSupplierData, self).create(vals)

    def _create_xml_id(self, xml_id, res_id, model):
        virtual_module_name = 'ptd'
        self._cr.execute(
            'INSERT INTO ir_model_data (module, name, res_id, model) \
            VALUES (%s, %s, %s, %s)',
            (virtual_module_name, xml_id, res_id, model))

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('supplier_code'):
            self.act_supplier_code()
        return res

    @api.multi
    def act_supplier_code(self):
        for data in self:
            supplier_domain=[('res_id', '=', data.supplier_id.id), ('model', '=', 'res.partner')]
            supplier_xml_id = self.env['ir.model.data'].search(supplier_domain, limit=1).name.replace('.', '_')
            spd_domain = [('res_id', '=', data.id), ('model', '=', self._name)]
            self.env['ir.model.data'].search(spd_domain).unlink()
            self._cr.execute('INSERT INTO ir_model_data (module, name, res_id, model) VALUES (%s, %s, %s, %s)',
                             ('spd', '{}_{}'.format(supplier_xml_id, data.supplier_code), data.id, self._name))

            partner_domain = [('res_id', '=', data.customer_supplier_id.id), ('model', '=', 'res.partner')]
            self.env['ir.model.data'].search(partner_domain).unlink()
            self._cr.execute('INSERT INTO ir_model_data (module, name, res_id, model) VALUES (%s, %s, %s, %s)',
                             ('rp', '{}_{}'.format(supplier_xml_id, data.supplier_code), data.customer_supplier_id.id, 'res.partner'))

    @api.multi
    def search_partner_id(self):
        for partner in self.filtered(lambda x: not x.customer_supplier_id.parent_id):
            domain = [('parent_id','=', False), ('comercial', 'ilike', '%G.{}%'.format(partner.customer_supplier_id.name.strip()))]
            new_partner = self.env['res.partner'].search(domain)
            print ("Buscando partner para {} con dominio {}: Encontrado {}".format(partner.customer_supplier_id.display_name, domain, new_partner))
            if len(new_partner) == 1:
                partner.customer_supplier_id.parent_id = new_partner.id
                partner.customer_supplier_id.message_post(body="Se ha añadido un nuevo parent automaticamente")


    @api.multi
    def update_partner_from_res_partner(self):
        for data in self.browse(self._context.get('active_ids', [])):
            data.customer_supplier_id.write({
                'external': True,
                'supplier_id': data.supplier_id.id,
                'supplier_code': data.supplier_code,
                'supplier_str': data.supplier_str,
                'supplier_customer_ranking_id': data.supplier_customer_ranking_id.id,
                'parent_id': data.partner_id.id
            })

