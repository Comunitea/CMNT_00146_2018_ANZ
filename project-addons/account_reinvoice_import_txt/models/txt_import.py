# -*- coding: utf-8 -*-
# © 2018 Comunitea Servicios Tecnologicos (<http://www.comunitea.com>)
# Kiko Sanchez (<kiko@comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, tools, api, _

from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta
from odoo.addons import decimal_precision as dp
import os
import pprint
ODOO_READ_FOLDER = 'Send'
ODOO_END_FOLDER = 'Receive'
ODOO_WRITE_FOLDER = 'temp'

ODOO_FOLDER_TXT = "/opt/hotfolder/invoice_txt/txt"
ODOO_FOLDER_ARCHIVE = "/opt/hotfolder/invoice_txt/done"
ODOO_FOLDER_ERROR = "/opt/hotfolder/invoice_txt/error"



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

def is_number_line(str, num_actual_linea=False):
    num = str.strip()
    if num:
        num = num.isdigit() and int(num) or 0
    return num == num_actual_linea





def get_num(str, force_int=False):

    if str.strip():
        num_str = str.strip().replace(',', '.').split('.')
        entero = num_str[0].isdigit() and int(num_str[0]) or 0

        if len(num_str) == 1 or force_int:
            return entero
        decimales = num_str[1].isdigit() and int(num_str[1]) or 0.00
        if decimales < 10:
            dec = decimales / 10
        elif decimales < 100:
            dec = decimales / 100
        else:
            dec = decimales / 1000
        return entero + dec
    return 0.00



class InvoiceTxtImportLine(models.Model):

    _name = "invoice.txt.import.line"

    num_linea = fields.Integer('Linea')
    product_id = fields.Many2one('product.product')
    articulo = fields.Char('Articulo')
    codigo = fields.Char("Articulo")
    descripcion = fields.Char("Description")
    descuento = fields.Char("Descuentos %")
    descuento_str_total = fields.Char("Descuento en cadena")
    qty = fields.Integer ('Cantidad total')
    descripcion_qty = fields.Char('Tallas')
    precio_articulo = fields.Float(string='Precio artículo', required=True, digits=dp.get_precision('Product Price'))
    valor_neto = fields.Float(string='Valor neto total', required=True, digits=dp.get_precision('Product Price'))
    invoice_txt_import_id = fields.Many2one('invoice.txt.import')
    message_line = fields.Char("Txt de la linea")
    state_country = fields.Char("Pais de origen")
    partida_arancelaria = fields.Char("Partida arancelaria")
    order_id = fields.Many2one('invoice.txt.import.order')


    def get_line_vals(self, invoice_id=False):
        return {'product_id': self.product_id or False,
                'quantity': self.qty,
                'price_unit': self.precio_articulo,
                'discount': self.descuento,
                'name': self.descripcion + self.descripcion_qty,
                'invoice_id': invoice_id}

class InvoiceTXTImportOrder(models.Model):

    _name ="invoice.txt.import.order"

    name = fields.Char("Nombre")
    fecha = fields.Date("Fecha")
    invoice_txt_import_id = fields.Many2one('invoice.txt.import')


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
    type = fields.Char('Type')
    supplier_picking_num = fields.Char("Numero de albarán")
    supplier_picking_date = fields.Date('Fecha de albarán')
    supplier_order_num = fields.Char('Numero de pedido')
    supplier_order_date = fields.Date("Fecha de pedido")

    arancel = fields.Char('Partida arancelaria')
    country = fields.Char('Pais de origen')
    partner_bank = fields.Char("Banco")
    bank_id = fields.Many2one('res.partner.bank', string='Partner Bank Account', required=False)
    account_position_id = fields.Many2one('account.fiscal.position',
                                                   string="Fiscal Position",
                                                   help="The fiscal position will determine taxes and accounts used for the partner.")
    desc_p_p = fields.Float(string='Descuento pp €', digits=dp.get_precision('Product Price'))
    desc_p_p_per_cent = fields.Float(string='Descuento pp %', digits=dp.get_precision('Product Price'))
    iva_per_cent = fields.Float(string='IVA %', digits=dp.get_precision('Product Price'))
    iva = fields.Float(string='IVA €', digits=dp.get_precision('Product Price'))
    equiv_per_cent = fields.Float(string='R. Equiv %', digits=dp.get_precision('Product Price'))
    equiv = fields.Float(string='R. Equiv €', digits=dp.get_precision('Product Price'))
    recargos = fields.Float(string='Recargos €', digits=dp.get_precision('Product Price'))
    fecha_vencimiento = fields.Date("Fecha de vencimiento")
    value_date = fields.Date("Fecha VAlor")
    num_lineas = fields.Integer("Numero de lineas")
    total_amount = fields.Float(string='Total factura', digits=dp.get_precision('Product Price'))
    valor_neto = fields.Float(string='Valor neto', digits=dp.get_precision('Product Price'))
    base_imponible= fields.Float(string='Base imponible', digits=dp.get_precision('Product Price'))
    invoice_line_txt_import_ids = fields.One2many('invoice.txt.import.line', 'invoice_txt_import_id', string="Lineas")
    refund_note = fields.Char("Nota/Motivo de abono")
    original_rectificatica= fields.Char("Rectifica ...")
    order_ids = fields.One2many('invoice.txt.import.order', 'invoice_txt_import_id', string="Pedidos")

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
            product_domain = ([('default_code', '=', 'AD.00000')])
            product_id = self.env['product.product'].search(product_domain, limit=1)
        return product_id or False


    @api.multi
    def get_associate_id_from_associate_name(self):

        for txt in self.filtered(lambda x:x.associate_name and not x.associate_id):
            obj = self.env['partner.supplier.data'].get_associate_id_from_str(txt.associate_name)

            if obj:
                txt.associate_id = obj
            else:
                txt.associate_id = False


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

        if self.associate_name:
            self.get_associate_id_from_associate_name()
            if not self.associate_id:
                message = "{} <li>{} {}</li>".format(message, 'No hay encuentro al asociado para el nombre ', self.associate_name)

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

    def get_pedido(self, str, type='adidas'):
        if type == 'adidas':
            pedido = str.split(':')
            ref_pedido = pedido[1].replace('Fecha', '').strip()
            fecha_pedido = get_odoo_date(pedido[2])
            new_pedido_vals = {'invoice_txt_import_id': self.id,
                               'name': ref_pedido,
                               'fecha': fecha_pedido}
            pedido = self.env['invoice.txt.import.order'].create(new_pedido_vals)
            print('Encuentrp pedido {}'.format(ref_pedido))
            return pedido


    def get_line(self, linea_pedido):

        descuento_str_total = linea_pedido[85:100].strip()

        if descuento_str_total != '':
            descuento = 0.00
            for d1 in descuento_str_total.split(' '):
                descuento += get_num(d1.strip())
        else:
            descuento = 0.00


        codigo = linea_pedido[4:14].strip()
        num_linea = get_num(linea_pedido[0:4].strip())
        descripcion = linea_pedido[14:82].replace(codigo, '').strip()
        tallas = linea_pedido[110:190].strip()
        qty = tallas.split(' ')[0]
        euros = clear_str(linea_pedido).split(' ')
        valor_neto = get_num(euros[len(euros)-1].strip())
        precio_articulo = get_num(euros[len(euros)-2].strip())

        articulo = '[{}] {}'.format(codigo, descripcion)
        descripcion = '{} {}'.format(articulo.strip(), tallas)

        val = {'num_linea': num_linea,
               'codigo': codigo,
               'articulo': articulo,
               'descripcion': descripcion,
               'qty': qty,
               'descripcion_qty': tallas,
               'precio_articulo': precio_articulo,
               'descuento': descuento,
               'descuento_str_total': descuento_str_total,
               'valor_neto': valor_neto,
               'message_line': clear_str(linea_pedido)}
        return val

    @api.multi
    def import_txt_invoice(self):


        ts = ['adidas', 'nike', 'joma']
        routes = [roots for roots in os.walk(ODOO_FOLDER_TXT, topdown=True)]
        for roots in routes:
            fold = roots[0]
            for file_name in roots[2]:
                origin = os.path.join(fold, file_name)
                print ('Fichero: {}'.format(origin))
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

        domain= [('file_name', '=', file_name)]
        val = {'file_name': file_name,
               'supplier_invoice_num': file_name}
        txt_obj = self.search(domain, limit=1)
        option = "create"
        if txt_obj:
            txt_obj.unlink()
            option = "rewrite"


        txt_obj = self.create(val)
        txt_obj.message_post(body="{} {}".format(option =='create' and "Nuevo" or "Actualizado", datetime.now()))
        if txt_obj:

            if type=='nike':
                return txt_obj.check_nike(str, file_name)
            elif type == 'adidas':
                return txt_obj.check_adidas(str, file_name)
        return False

    def check_nike(self, str, file_name):
        return False

    def check_adidas(self, str, file_name):


        print ("\nFichero de factura: {}".format(file_name))
        longitud_fichero = len(str)

        if str[1].find('ABONO') > -1:
            type='in_refund'
        else:
            type = 'in_invoice'

        original_rectificatica = ''
        clienteno = str[3][167:225].strip()
        facturano = str[4][167:225].strip()
        fecha_factura=  str[5][167:200].strip()
        fecha_factura = get_odoo_date(fecha_factura)

        if type=='in_invoice':
            value_date = str[6][167:200].strip()
            value_date = get_odoo_date(value_date)
            pay_notes = str[9][167:].strip()
        else:
            value_date = fecha_factura
            original_rectificatica = str[6][167:225].strip()


        partner_nif  = str[7][167:225].strip()
        pay_notes = str[9][167:].strip()
        eori = str[10][233:].strip()
        ###DATOS DE ALBAŔAN

        index = 17
        print ("Linea: {} > {} ".format(index, str[index].strip()))
        supplier_picking_num = albaran = partner_bank = fecha_albaran = associate_name = region = ref_pedido = fecha_vencimiento = fecha_pedido = value_date=refund_note=False

        if type == 'in_invoice':
            if str[index].strip() and str[index].strip().find('Albar') >-1:
                albaran = str[index].split(':')[1].strip()
                if albaran:
                    datos_albaran = albaran.split()
                    supplier_picking_num = datos_albaran[0]
                    fecha_albaran = datos_albaran[1]
                    fecha_albaran = get_odoo_date(fecha_albaran)
                    index += 2
                    if str[index].strip().find('Nombre') >-1:
                        associate_name = str[index].split(':')[1].strip()
                        index += 2
                    if str[index].strip().find('Regi') >-1:
                        region = str[index].split(':')[1].strip()
                        index += 2
            else:
                self.message_post(body="No he encontrado los datos del albarán donde esperaba")
                return False

        ### DATOS DE LAS LINEAS
        lineas=[]

        line_count = 1
        is_line = True
        index = 17
        pedido = False
        print ("Busco líneas: {} > {} para una factura {}".format(index, str[index].strip(), type))
        while is_line:
            print("Linea: {} > {} ".format(index, str[index].strip()))
            if not str[index].strip():
                index += 1
                continue

            if str[index].find('Valor neto total') > -1:
                is_line = False
                continue
            if type == 'in_invoice' and str[index].find('Su pedido no.') > -1:# str[index].split(':')[0].strip() == 'Su pedido no.':
                pedido = self.get_pedido(str[index].strip(), 'adidas')
                print('Encuentro y creo pedido {}'.format(pedido.name))
                index += 1
            elif type == 'in_refund' and line_count == 1 and not is_number_line(str[index][:4], line_count):
                refund_note = str[index].strip()
                print('Refund note {}'.format(refund_note))
                index += 1
            else:
                print ("Busco una linea con indice {} en {}:".format(line_count, str[index]))
                if is_number_line(str[index][:4], line_count):
                    print("--->Encuentro: {}:".format(str[index]))
                    linea = self.get_line(str[index])
                    if pedido:
                        linea.update(order_id=pedido.id)
                    line_count += 1
                    if str[index].find('Partida arancelaria') > -1:# str[index+2][19:38] == 'Partida arancelaria':
                        index += 2
                        linea.update(partida_arancelaria=str[index][39:].strip())
                        if str[index+2].find('s de origen:') > -1:
                            index += 2
                            linea.update(state_country=str[index][34:].strip())
                    lineas.append(linea)
                index += 1

            if index >= longitud_fichero:
                self.message_post('Error leyendo las líneas del fichero')
                return False

        ## saco cuadro de factura
        print ("FIN LINEAS en linea {}: {}".format(index, str[index]))
        valor_neto = get_num(str[index][-8:])
        index += 1
        recargos = get_num(str[index][-8:])

        index += 1
        desc_p_p = get_num(str[index][-8:])
        desc_p_p_cent = get_split(str[index])[0].strip().split(' ')[0]
        desc_p_p_cent = get_num(desc_p_p_cent)
        index += 1
        if str[index].find('Banco cliente')>-1:
            partner_bank = get_split(str[index])[1]
        base_imponible = get_num(str[index][-8:].strip())

        index += 1
        iva = get_num(str[index][-8:])
        iva_per_cent = get_num(get_split(str[index])[0].strip().split(' ')[0])
        if str[index].find('Fecha vencimiento')>-1:
            vencimientos = []
            fecha_vencimiento = get_odoo_date(str[index+2][30:50].strip())
            importe_vencimineto = get_num(str[index+2][80:].strip())
            vencimientos.append({'fecha_vencimiento': fecha_vencimiento, 'importe_vencimiento': importe_vencimineto})
            if str[index+3][30:50].strip() and len(str[index+3])<100:
                fecha_vencimiento = get_odoo_date(str[index+3][30:50].strip())
                importe_vencimineto = get_num(str[index+3][80:].strip())
                vencimientos.append(
                    {'fecha_vencimiento': fecha_vencimiento, 'importe_vencimiento': importe_vencimineto})
                if str[index + 4][30:50].strip()  and len(str[index+4])<100:
                    fecha_vencimiento = get_odoo_date(str[index + 4][30:50].strip())
                    importe_vencimineto = get_num(str[index + 4][80:].strip())
                    vencimientos.append(
                        {'fecha_vencimiento': fecha_vencimiento, 'importe_vencimiento': importe_vencimineto})
        index += 1
        equiv = get_num(str[index][-8:])
        equiv_per_cent = get_num(get_split(str[index])[0].strip().split(' ')[0])
        inc = index
        is_total = False
        while not is_total:
            if str[inc].find('TOTAL FACTURA')>-1 or str[inc].find('TOTAL ABONO')>-1:
                total = get_num(str[inc][-8:])
                is_total = True
            if inc-index > 10:
                is_total = True
                total = 0.00
            else:
                inc+=1

            if inc >= longitud_fichero:
                self.message_post('Error leyendo el total de la factura')
                return False

        txt_invoice_val = {
            'file_name': file_name,
            'eori': eori,
            'partner_id': False,
            'associate_name': associate_name,
            'region': region,
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
            'partner_bank': partner_bank,
            'recargos': recargos,
            'state': 'draft',
            'desc_p_p': desc_p_p,
            'desc_p_p_per_cent': desc_p_p_cent,
            'iva_per_cent': iva_per_cent,
            'iva': iva,
            'equiv_per_cent': equiv_per_cent,
            'equiv': equiv,
            'fecha_vencimiento': fecha_vencimiento,
            'value_date': value_date or fecha_albaran,
            'num_lineas': line_count,
            'total_amount': total,
            'type': type,
            'refund_note': refund_note,
            'original_rectificatica':original_rectificatica

        }



        self.write_invoice_from_txt(txt_invoice_val, lineas)
        if not self:
            self.message_post(body="error al escribir los valores en el invoice txt")
            return False
        if not self.partner_id:
            self.message_post(body="No se ha encontrado un partner")
            return False
        else:
            return True
            new_invoice = self.create_invoice_from_invoice_txt()
            if not new_invoice:
                self.message_post(body="Error al crear la factura asociada en odoo")
                self.state = 'error'
                return False

        return True




    def write_invoice_from_txt(self, txt_invoice_val, lineas):
        self.write(txt_invoice_val)
        self.get_partner_refs()
        self.invoice_line_txt_import_ids.unlink()
        for linea in lineas:
            product_id = self.get_product(linea, self.partner_id.id)
            linea.update(invoice_txt_import_id=self.id,
                         product_id = product_id and product_id.id)
            self.env['invoice.txt.import.line'].create(linea)
        return True


    @api.multi
    def create_invoice_from_invoice_txt(self):
        for txt in self:

            txt.get_partner_refs()
            refund_invoice_id = False
            txt.state = 'error'
            if not txt.partner_id:
                txt.message_post(body="No encuentro proveedor, asociado")
                return False
            if self.type == 'in_refund':
                refund_invoice_id = self.env['account.invoice'].search([('reference', '=', self.original_rectificatica.split())])
                if refund_invoice_id:
                    txt.associate_id = refund_invoice_id.associate_id
                    txt.associate_id = refund_invoice_id.associate_id.name

            currency_id = txt.associate_id.property_product_pricelist.currency_id and txt.associate_id.property_product_pricelist.currency_id.id or txt.partner_id.property_product_pricelist.currency_id.id
            if not currency_id:
                txt.message_post(body="No encuentro moneda")
                return False
            journal_id = txt.env['account.journal'].search([('name', '=', 'Refacturas')])
            if not journal_id:
                txt.message_post(body="No encuentro diario de refacturas")
                return False
            invoice_val = {
                'type': self.type or 'in_invoice',
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
                'check_total': txt.total_amount,
                'date_invoice_from_associate_order': txt.supplier_picking_date,
                'refund_invoice_id': refund_invoice_id
            }
            ## TODO NO ENTIENDO ESTO

            if not txt.account_position_id:
                txt.account_position_id =  txt.associate_id.property_account_position_id or txt.partner_id.property_account_position_id

            invoice = self.env['account.invoice'].new(invoice_val)
            invoice._onchange_partner_id()
            inv = invoice._convert_to_write(invoice._cache)
            inv.update(journal_id = journal_id.id,
                       fiscal_position_id = txt.account_position_id.id )
            new_invoice = self.env['account.invoice'].create(inv)
            new_invoice.journal_id = journal_id
            new_invoice.date_due = txt.fecha_vencimiento
            txt.invoice_id = new_invoice
            property_account_position_id = txt.account_position_id

            #if 'Recargo' in property_account_position_id:
            #    new_invoice.fiscal_position_id = False
            #else:
            #    new_invoice.fiscal_position_id = property_account_position_id

            print ("\n------------\nFACTURA PARA : {}\n------------\n".format(new_invoice.associate_id.name or self.partner_id.name))

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
