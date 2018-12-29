# -*- coding: utf-8 -*-
# © 2018 Comunitea Servicios Tecnologicos (<http://www.comunitea.com>)
# Kiko Sanchez (<kiko@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, tools, api, _

from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from odoo.addons import decimal_precision as dp
import os

ODOO_READ_FOLDER = 'Send'
ODOO_END_FOLDER = 'Receive'
ODOO_WRITE_FOLDER = 'temp'

ODOO_FOLDER_TXT = "/opt/odoo/txt"
ODOO_FOLDER_ARCHIVE = "/opt/odoo/archive"
ODOO_FOLDER_ERROR = "/opt/odoo/error"


def get_odoo_date(str):
    fecha_str = str.strip()
    day = fecha_str[0:2]
    mes = fecha_str[3:5]
    año = fecha_str[6:10]
    date = "{}-{}-{}".format(año, mes, day)
    return date


def get_split(str, to_split='  '):
    str_ = str.split(to_split)
    res = []
    for s in str_:
        if len(s) > 0:
            res.append(s)
    return res


def clear_str(str):
    str = get_split(str, ' ')
    clear = ''
    for s in str:
        clear = '{} {}'.format(clear, s)

    return clear.strip()


def get_num(str):
    num_str = str.strip().replace(',', '.').split('.')
    if len(num_str) == 1:
        return int(num_str[0])
    decimales = int(num_str[1])

    if decimales < 10:
        dec = decimales / 10
    elif decimales < 100:
        dec = decimales / 100
    else:
        dec = decimales / 1000
    return int(num_str[0]) + dec


def get_line(linea_pedido):
    tiene_descuento = False
    if linea_pedido[90:94].strip() != '':
        tiene_descuento = True
    codigo = linea_pedido[0:14].split(' ')[1].strip()
    old_pedido = linea_pedido.split('  ')
    pedido = []
    for p in old_pedido:
        if len(p.strip()) > 0:
            pedido.append(p)

    pedido1 = pedido
    max = len(pedido) - 1

    valor_neto_str = pedido[max].strip()
    valor_neto = get_num(valor_neto_str)
    pedido.pop(max)

    precio_articulo_str = pedido[max - 1].strip()
    precio_articulo = get_num(precio_articulo_str)
    pedido.pop(max - 1)

    tallas = pedido[max - 2].strip()
    qty = tallas[0].strip()
    pedido.pop(max - 2)

    if tiene_descuento:
        # en adidas puede ser 2
        descuento_str_total = pedido[max - 3].strip()
        descuento = 0.00
        for d1 in descuento_str_total.split(' '):
            descuento_str = d1.strip()
            descuento += get_num(descuento_str)

        pedido.pop(max - 3)
    else:
        descuento = 0.00

    num_linea = get_num(pedido[0].strip())
    pedido.pop(0)

    codigo = linea_pedido[0:14].split()[1]
    articulo = ''
    for str in pedido:
        articulo = '{} {}'.format(articulo, str)

    descripcion = articulo.strip()

    val = {'num_linea': num_linea,
           'codigo': codigo,
           'descripcion': descripcion,
           'qty': qty,
           'descripcion_qty': tallas,
           'precio_articulo': precio_articulo,
           'descuento': descuento,
           'valor_neto': valor_neto}

    return val

class InvoiceTxtImportLine(models.Model):

    _name = "invoice.txt.import.line"

    num_linea = fields.Integer('Linea')
    product_id = fields.Many2one('product.product')
    codigo = fields.Char("Articulo")
    descripcion = fields.Char("Description")
    descuento = fields.Char("Descuentos %")
    qty = fields.Integer ('Cantidad total')
    descripcion_qty = fields.Char('Tallas')
    precio_articulo = fields.Float(string='Precio artículo', required=True, digits=dp.get_precision('Product Price'))
    valor_neto = fields.Float(string='Valor neto total', required=True, digits=dp.get_precision('Product Price'))
    invoice_txt_import_id = fields.Many2one('invoice.txt.import')


    def get_line_vals(self, invoice_id=False):
        return {'product_id': self.product_id or False,
                'quantity': self.qty,
                'price_unit': self.precio_articulo,
                'discount': self.descuento,
                'name': self.descripcion + self.descripcion_qty,
                'invoice_id': invoice_id}


class InvoiceTxtImport(models.Model):

    _name ="invoice.txt.import"
    _inherit = ['mail.thread']

    @api.multi
    def name_get(self):
        if not self:
            super(InvoiceTxtImport, self).name_get()
        res=[]
        for txt in self:
            name = "{} -> {} : {}".format(txt.partner_id and txt.partner_id.name or txt.partner_vat, txt.associate_id and txt.associate_id.name or txt.associate_name,  txt.supplier_invoice_num)
            res.append((txt.id, name))


        return res




    file_name = fields.Char('File name')
    eori = fields.Char('NIF Proveedor')
    type = fields.Selection([('AD', 'Adidas'),
                             ('JM', 'Joma')])
    file_date = fields.Char("File date")
    invoice_id = fields.Many2one('account.invoice')
    associate_name = fields.Char("Nombre asociado")
    associate_id = fields.Many2one('res.partner', 'Asociado')

    partner_vat = fields.Char("Nif cliente")
    partner_id = fields.Many2one('res.partner', 'Proveedor')

    supplier_partner_num = fields.Char("Numero de cliente")
    state = fields.Selection([('draft', 'Borrador'), ('invoiced', 'Facturado'), ('error', 'Error')])

    state_country = fields.Char("Región")

    supplier_invoice_num = fields.Char("Numero de factura de proveedor")
    supplier_invoice_date = fields.Date("Fecha factura de proveedor")

    supplier_partner_nif = fields.Char("Nif cliente")
    pay_notes = fields.Char("Nota de pago")

    supplier_picking_num = fields.Char("Numero de albarán")
    supplier_picking_date = fields.Date('Fecha de albarán')
    supplier_order_num = fields.Char('Numero de pedido')
    supplier_order_date = fields.Date("Fecha de pedido")

    arancel = fields.Char('Partida arancelaria')
    country = fields.Char('Pais de origen')
    partner_bank = fields.Char("Banco")
    bank_id = fields.Many2one('res.partner.bank', string='Partner Bank Account', required=False)

    desc_p_p = fields.Float(string='Descuento pp €', digits=dp.get_precision('Product Price'))
    desc_p_p_per_cent = fields.Float(string='Descuento pp %', digits=dp.get_precision('Product Price'))
    iva_per_cent = fields.Float(string='IVA %', digits=dp.get_precision('Product Price'))
    iva = fields.Float(string='IVA €', digits=dp.get_precision('Product Price'))
    equiv_per_cent = fields.Float(string='R. Equiv %', digits=dp.get_precision('Product Price'))
    equiv = fields.Float(string='R. Equiv €', digits=dp.get_precision('Product Price'))
    recargos = fields.Float(string='Recargos €', digits=dp.get_precision('Product Price'))
    fecha_vencimiento = fields.Date("Fecha de vencimiento")
    num_lineas = fields.Integer("Numero de lineas")
    total_amount = fields.Float(string='Total factura', digits=dp.get_precision('Product Price'))
    valor_neto = fields.Float(string='Valor neto', digits=dp.get_precision('Product Price'))
    base_imponible= fields.Float(string='Base imponible', digits=dp.get_precision('Product Price'))
    invoice_line_txt_import_ids = fields.One2many('invoice.txt.import.line', 'invoice_txt_import_id', string="Lineas")



    def check_existing_txt(self):
        self.env['invoice.txt.import'].import_txt_invoice()

    def get_product(self, linea, partner_id=False):

        product_id = False
        # Busco en product suplier info
        if partner_id:
            domain = [('product_code', '=', linea['codigo']), ('name', '=', partner_id)]
            product_supplierinfo = self.env['product.supplierinfo'].search(domain, limit=1)
            if product_supplierinfo:
                product_id = product_supplierinfo.product_id
        # Busco en default_code
        if not product_id:
            product_domain = ([('default_code', '=', linea['codigo'])])
            product_id = self.env['product.product'].search(product_domain, limit=1)
        # Busco en el nombre
        if not product_id:
            product_domain = ([('name', 'ilike', '%{}%'.format(linea['codigo']))])
            product_id = self.env['product.product'].search(product_domain, limit=1)
        # Busco en uno auxiliar
        if not product_id:
            product_domain = ([('default_code', '=', 'AUX_IMPORT_TXT')])
            product_id = self.env['product.product'].search(product_domain, limit=1)
        return product_id or False


    def get_partner_refs(self):

        if not self.partner_vat:
            self.message_post(body='No hay NIF del proveedor')
            return
        p = self.partner_vat.replace('ES', '')
        message = "<ul>"
        domain = [('vat', 'ilike', '%{}%'.format(p))]
        self.partner_id = self.env['res.partner'].search(domain, limit=1)
        if not self.partner_id:
            message = "{} <li>{}</li>".format(message, 'No hay proveedor')


        domain = [('code', '=', self.associate_name), ('supplier_id', '=', self.partner_id.id)]
        obj = self.env['supplier.code.txt.import'].search(domain, limit=1)
        if obj and obj.customer_id:
            self.associate_id = obj.customer_id
        else:
            message = "{} <li>{}</li>".format(message, 'No hay encuentro al asociado por codigo')

            associate_domain = [('name', '=', self.associate_name)]
            self.associate_id = self.env['res.partner'].search(associate_domain, limit=1)
            if not self.associate_id:
                message = "{} <li>{}</li>".format(message, 'No hay encuentro al asociado por nombre')
                message = "{} <li>{}</li>".format(message,'</ul>')

        if not(self.partner_id and self.associate_id):
            self.message_post(body=message)

    def predict_encoding(self, file_path, n_lines=30):
        '''Predict a file's encoding using chardet'''

        # Open the file as binary data
        try:
            import chardet
            with open(file_path, 'rb') as f:
                # Join binary lines for specified number of lines
                rawdata = b''.join([f.readline() for _ in range(n_lines)])

            return chardet.detect(rawdata)['encoding']

        finally:

            return False


    def import_txt_invoice(self):
        import io
        ts = ['adidas', 'nike']
        routes = [roots for roots in os.walk(ODOO_FOLDER_TXT, topdown=True)]
        for roots in routes:
            fold = roots[0]
            for file_name in roots[2]:
                origin = os.path.join(fold, file_name)
                type = fold.replace(ODOO_FOLDER_TXT + '/', '')
                enconding = self.predict_encoding(origin) or 'utf8'
                if type in ts:
                    file = open(origin, 'r', encoding=enconding,  errors="ignore")
                    file_obj = file.readlines()
                    file.close()
                    res = self.check(file_obj, file_name, type)
                else:
                    res= False

                if res:
                    dst = os.path.join(ODOO_FOLDER_ARCHIVE, file_name)
                else:
                    dst = os.path.join(ODOO_FOLDER_ERROR, file_name)

                os.rename(origin, dst)



    def check(self, str, file_name, type='NO'):
        if type=='nike':
            return self.check_nike(str, file_name)
        elif type == 'adidas':
            return self.check_adidas(str, file_name)
        return False

    def check_nike(self, str, file_name):
        return False

    def check_adidas(self, str, file_name):

        clienteno = str[3][167:225].strip()
        facturano = str[4][167:225].strip()
        fecha_factura=  str[5][167:200].strip()
        fecha_factura = get_odoo_date(fecha_factura)
        partner_nif  = str[7][167:225].strip()
        pay_notes = str[9][167:225].strip()
        eori = str[10][234:].strip()

        state_country = str[21].strip().split(':')[1]
        albaran = get_split(str[17], ' ')

        if albaran:
            supplier_picking_num = albaran[1]
            fecha_albaran = albaran[2]
            fecha_albaran = get_odoo_date(fecha_albaran)

        associate_name = clear_str(str[19][27:].strip())

        pedido = str[23][19:]
        pedido = pedido.replace('Su pedido no.:', '')
        pedido = pedido.split('Fecha:')
        ref_pedido = pedido[0]
        fecha_pedido = pedido[1]
        fecha_pedido = get_odoo_date(fecha_pedido)
        lineas=[]
        index = 25
        line_count = 0
        is_line = True
        while is_line:
            if len(str[index][:4].strip()) > 0:
                linea = get_line(str[index])
                line_count+=1
                lineas.append(linea)
            else:
                is_line = False
            index +=1
        partida_arancelaria = state_country = ''
        if str[index][19:38] == 'Partida arancelaria':
            partida_arancelaria = str[index][39:].strip()
            index+=2
            state_country = str[index+2][34:].strip()
            index += 2
        valor_neto = get_num(get_split(str[index])[1])
        index+=1
        recargos = get_num(get_split(str[index])[1])
        index += 1
        desc_p_p = get_num(get_split(str[index])[1])
        index +=1
        desc_p_p_cent = get_split(str[index])[0].strip().split(' ')[0]

        partner_bank = get_split(str[index])[1]
        base_imponible = get_num(get_split(str[index])[3])
        index+=1
        iva = get_num(get_split(str[index])[4])
        iva_per_cent = get_num(get_split(str[index])[3].strip().split(' ')[0])
        index += 1
        equiv = get_num(get_split(str[index])[1])
        equiv_per_cent = get_num(get_split(str[index])[0].strip().split(' ')[0])
        index += 1
        fecha_vencimiento = get_odoo_date(get_split(str[index])[0])

        index+=1
        total = get_num(get_split(str[index])[1])


        pais_origen = str[index][19:39]
        if len(pais_origen.strip())>0:
            index += 2
            pais_origen = str[index].strip().split(':')[1]
        else:
            pais_origen = ''

        txt_invoice_val = {
            'file_name': file_name,
            'eori': eori,
            'partner_id': False,

            'associate_name': associate_name,
            'partner_vat': eori,
            'supplier_partner_num': clienteno,
            'supplier_invoice_num': facturano,
            'supplier_invoice_date': fecha_factura,
            'supplier_partner_nif': partner_nif,
            'pay_notes': pay_notes,
            'valor_neto': valor_neto,
            'base_imponible': base_imponible,
            'supplier_picking_num': supplier_picking_num,
            'supplier_picking_date': fecha_albaran,
            'supplier_order_num': ref_pedido,
            'supplier_order_date':  fecha_pedido,
            'arancel': partida_arancelaria,
            'country': pais_origen,
            'partner_bank': partner_bank,
            'recargos': recargos,
            'state': 'draft',
            'state_country': state_country,
            'desc_p_p': desc_p_p,
            'desc_p_p_cent': desc_p_p_cent,
            'iva_per_cent': iva_per_cent,
            'iva': iva,
            'equiv_per_cent': equiv_per_cent,
            'equiv': equiv,
            'fecha_vencimiento': fecha_vencimiento,
            'num_lineas': line_count,
            'total_amount': total
        }


        invoice = self.create_invoice_from_txt(txt_invoice_val, lineas)
        if not invoice:
            return False
        if invoice:
            new_invoice=False
            try:
                new_invoice = invoice.create_invoice_from_invoice_txt()
            finally:
                a=1
            if not new_invoice:
                invoice.state = 'error'
                return False
        return True




    def create_invoice_from_txt(self, txt_invoice_val, lineas):
        new_txt_invoice = self.env['invoice.txt.import'].create(txt_invoice_val)
        new_txt_invoice.get_partner_refs()

        for linea in lineas:
            product_id = self.get_product(linea, self.partner_id.id)
            linea.update(invoice_txt_import_id=new_txt_invoice.id,
                         product_id = product_id and product_id.id)
            self.env['invoice.txt.import.line'].create(linea)
        return new_txt_invoice


    @api.multi
    def create_invoice_from_invoice_txt(self):

        for txt in self:
            txt.get_partner_refs()
            txt.state = 'error'
            if not txt.associate_id or not txt.partner_id:
                txt.message_post(body="No encuentro proveedor, asociado")
                return False

            currency_id = txt.associate_id.property_product_pricelist.currency_id and txt.associate_id.property_product_pricelist.currency_id.id
            if not currency_id:
                txt.message_post(body="No encuentro moneda")
                return False
            journal_id = txt.env['account.journal'].search([('name', '=', 'Refacturas')])
            if not journal_id:
                txt.message_post(body="No encuentro diario de refacturas")
                return False
            invoice_val = {
                'type': 'in_invoice',
                'partner_id': txt.partner_id.id or False,
                'supplier_invoice_number': txt.supplier_invoice_num,
                'reference': txt.supplier_invoice_num,
                'currency_id': currency_id,
                'associate_id': txt.associate_id.id or False,
                'journal_id': journal_id and journal_id[0].id or False,
                'date_invoice': txt.supplier_invoice_date,
                'date_due': txt.fecha_vencimiento,
                'company_id': 1,
                'operating_unit_id': journal_id.operating_unit_id.id,
                'check_total': txt.total_amount
            }
            invoice = self.env['account.invoice'].new(invoice_val)

            invoice._onchange_partner_id()
            inv = invoice._convert_to_write(invoice._cache)
            inv.update(journal_id = journal_id.id, fiscal_position_id= txt.associate_id.property_account_position_id.id, )
            new_invoice = self.env['account.invoice'].create(inv)
            new_invoice.journal_id = journal_id
            new_invoice.date_due = txt.fecha_vencimiento
            txt.invoice_id = new_invoice
            if 'Recargo' in txt.associate_id.property_account_position_id.name:
                new_invoice.fiscal_position_id = False
            else:
                new_invoice.fiscal_position_id = txt.associate_id.property_account_position_id



            print ("\n\n----------------\nFACTURA PARA : {}\n\n----------------\n".format(new_invoice.associate_id.name))
            for linea in txt.invoice_line_txt_import_ids:
                vals = linea.get_line_vals(new_invoice.id)
                invoice_line = self.env['account.invoice.line'].new(vals)
                invoice_line._onchange_product_id()
                invoice_line.invoice_line_tax_ids = new_invoice.fiscal_position_id.map_tax(invoice_line.invoice_line_tax_ids, invoice_line.product_id,
                                                                                           new_invoice.associate_id)
                invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.ids

                inv_line = invoice_line._convert_to_write(invoice_line._cache)
                inv_line.update(name=vals['name'], price_unit=linea['precio_articulo'], discount=linea['descuento'])
                self.env['account.invoice.line'].create(inv_line)

            new_invoice.compute_taxes()

            message = _("Esta factura ha sido creada desde el fichero: <a href=# data-oe-model=invoice.txt.import data-oe-id=%d>%s</a>") % (txt.id, txt.file_name)
            txt.state = 'invoiced'
            new_invoice.message_post(body=message)

        return new_invoice