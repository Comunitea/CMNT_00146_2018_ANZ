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
    date = ''
    if fecha_str:
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
    str = str.strip()
    try:
        res = float(str.replace('.', '').replace(',', '.'))
        return res
    except Exception:
        return 0.00

class InvoiceWzd(models.TransientModel):

    _inherit = 'reinvoice.wzd'

    def get_invoices_values(self, inv):
        vals = super().get_invoices_values(inv)
        if inv.import_txt_id:
            vals.update(partner_shipping_id=inv.partner_shipping_id and inv.partner_shipping_id.id or inv.associate_id.id)
        return vals


class InvoiceTxtImportLine(models.Model):

    _name = "invoice.txt.import.line"

    num_linea = fields.Integer('Linea')
    product_id = fields.Many2one('product.product', 'Producto')
    articulo = fields.Char('Artículo')
    codigo = fields.Char("Código")
    descripcion = fields.Char("Description")
    descuento = fields.Float("Descuentos %", digits=dp.get_precision('Product Price'))
    descuento_str_total = fields.Char("Descuento en cadena")
    qty = fields.Integer ('Cantidad total')
    descripcion_qty = fields.Char('Tallas')
    precio_articulo = fields.Float(string='Precio artículo', required=True, digits=dp.get_precision('Product Price'))
    valor_neto = fields.Float(string='Valor neto total', required=True, digits=dp.get_precision('Product Price'))
    invoice_txt_import_id = fields.Many2one('invoice.txt.import', string="Fichero original")
    message_line = fields.Char("Txt de la linea")
    state_country = fields.Char("Pais de origen")
    partida_arancelaria = fields.Char("Partida arancelaria")
    order_id = fields.Many2one('invoice.txt.import.order', 'Importado de ...')


    def get_line_vals(self, invoice_id=False):
        return {'product_id': self.product_id or False,
                'quantity': self.qty,
                'price_unit': self.precio_articulo,
                'discount': self.descuento,
                'name': self.descripcion + self.descripcion_qty,
                'imported_price_subtotal': self.valor_neto,
                'invoice_id': invoice_id}


    @api.onchange('descuento_str_total')
    def onchenge_descuento_str_total(self):
        self.descuento = self.get_descuento_from_str(self.descuento_str_total)

    def get_descuento_from_str(self, descuento_str_total=False):
        if descuento_str_total and descuento_str_total != '':
            descuento = 0.00
            descuento_str_total = descuento_str_total.replace('.', ',')

            for d1 in descuento_str_total.split(' '):
                descuento += get_num(d1)
        else:
            descuento = 0.00

        return descuento

class InvoiceTXTImportOrder(models.Model):

    _name ="invoice.txt.import.order"
    _order = "fecha desc"

    name = fields.Char("Nombre")
    fecha = fields.Date("Fecha")
    invoice_txt_import_id = fields.Many2one('invoice.txt.import')



class PaymentDayTxt(models.Model):

    _name = 'payment.day.txt'

    @api.multi
    def name_get(self):
        res=[]
        for pay in self:
            name = "{} {} €".format(pay.date, pay.amount)
            res.append((pay.id, name))
        return res

    txt_id = fields.Many2one('invoice.txt.import', 'Importado de ...')
    amount = fields.Float(string='Importe', digits=dp.get_precision('Product Price'))
    date = fields.Date("Fecha")


class InvoiceTxtImport(models.Model):

    _name ="invoice.txt.import"
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    @api.multi
    def name_get(self):
        if not self:
            super(InvoiceTxtImport, self).name_get()
        res=[]
        for txt in self:
            name = "{} -> {} : {}".format(txt.partner_id and txt.partner_id.name or "Sin asociado",
                                          txt.partner_shipping_id and txt.partner_shipping_id.name or txt.associate_name,
                                          txt.supplier_invoice_num)
            res.append((txt.id, name))
        return res

    file_name = fields.Char('Fichero')
    eori = fields.Char('NIF Proveedor')
    type_supplier = fields.Selection([('AD', 'Adidas'),
                             ('JM', 'Joma')], string="Tipo")
    file_date = fields.Char("F. fichero")
    invoice_id = fields.Many2one('account.invoice', 'Factura')
    customer_invoice_id = fields.Many2one(related="invoice_id.customer_invoice_id")

    associate_name = fields.Char("Nombre importado", help="Nombre que aparece en la factura importada. Debe conincidir con el nombre del cliente externo, si lo hubiera")
    associate_id = fields.Many2one('res.partner', string='Empresa asociado')
    partner_shipping_id = fields.Many2one('res.partner', string='Asociado', domain=[('external','=', True)], help="Cliente externo que se asocia al nombre que se importad de la factura")

    partner_vat = fields.Char("NIF Cliente")
    partner_id = fields.Many2one('res.partner', 'Proveedor')

    supplier_partner_num = fields.Char("Numero de cliente")
    state = fields.Selection([('draft', 'Borrador'), ('invoiced', 'Facturado'), ('error', 'Error')], default='draft', string="Estado")

    state_country = fields.Char("Región")

    supplier_invoice_num = fields.Char("Nº factura")
    supplier_invoice_date = fields.Date("F. factura")

    supplier_partner_nif = fields.Char("Nif cliente")
    pay_notes = fields.Char("Plazos de pago")
    type = fields.Char('Type')
    supplier_picking_num = fields.Char("Numero de albarán")
    supplier_picking_date = fields.Date('F. albarán')
    supplier_order_num = fields.Char('Numero de pedido')
    supplier_order_date = fields.Date("F. pedido")

    arancel = fields.Char('Partida arancelaria')
    country = fields.Char('Pais de origen')
    partner_bank = fields.Char("Banco")
    payment_days = fields.Char("Vencimientos")
    bank_id = fields.Many2one('res.partner.bank', string='Banco (Odoo)', required=False)
    account_position_id = fields.Many2one('account.fiscal.position',
                                                   string="Posicion fiscal",)
    desc_p_p = fields.Float(string='Descuento pp €', digits=dp.get_precision('Product Price'))
    desc_p_p_per_cent = fields.Float(string='Descuento pp %', digits=dp.get_precision('Product Price'))
    iva_per_cent = fields.Float(string='IVA %', digits=dp.get_precision('Product Price'))
    iva = fields.Float(string='IVA €', digits=dp.get_precision('Product Price'))
    igic_per_cent = fields.Float(string='IGIC %', digits=dp.get_precision('Product Price'))
    igic = fields.Float(string='IGIC €', digits=dp.get_precision('Product Price'))
    equiv_per_cent = fields.Float(string='R. Equiv %', digits=dp.get_precision('Product Price'))
    equiv = fields.Float(string='R. Equiv €', digits=dp.get_precision('Product Price'))
    dua_per_cent = fields.Float(string='DUA %', digits=dp.get_precision('Product Price'))
    dua = fields.Float(string='DUA €', digits=dp.get_precision('Product Price'))
    recargos = fields.Float(string='Recargos €', digits=dp.get_precision('Product Price'))
    fecha_vencimiento = fields.Date("F. vencimiento")
    value_date = fields.Date("F. Valor")
    num_lineas = fields.Integer("Numero de lineas")
    total_amount = fields.Float(string='Total factura', digits=dp.get_precision('Product Price'))
    valor_neto = fields.Float(string='Valor neto', digits=dp.get_precision('Product Price'))
    base_imponible= fields.Float(string='Base imponible', digits=dp.get_precision('Product Price'))
    invoice_line_txt_import_ids = fields.One2many('invoice.txt.import.line', 'invoice_txt_import_id', string="Lineas")
    refund_note = fields.Char("Nota/Motivo de abono")
    original_rectificatica= fields.Char("Rectifica ...")
    order_ids = fields.One2many('invoice.txt.import.order', 'invoice_txt_import_id', string="Pedidos")
    payment_day_ids = fields.One2many('payment.day.txt', 'txt_id', string="Vencimientos")
    rule_ids = fields.One2many('reinvoice.rule', string="Reglas de descuentos", compute="get_reinvoice_rule_ids")


    @api.multi
    def write(self, vals):
        for txt in self:
            if txt.invoice_id:
                self.message_post("Se ha modificado este registro con la factura creada: Nuevos valores {}".format(vals))
        return super().write(vals)

    @api.onchange('partner_shipping_id')
    def onchange_partner_shipping_id(self):
        self.associate_id = self.partner_shipping_id.commercial_partner_id


    @api.onchange('associate_id')
    def onchange_associate_id(self):
        if self.associate_id:
            self.account_position_id = self.associate_id.property_account_position_id

    def check_existing_txt(self):
        self.env['invoice.txt.import'].import_txt_invoice()

    def get_product(self, linea, partner_id=False):
        product_domain = ([('default_code', '=', '01')])
        product_id = self.env['product.product'].search(product_domain, limit=1)
        return product_id or False

    def map_account_possition(self, account_position_id):
        if account_position_id and account_position_id.id == 4:
            account_position_id = self.env['account.fiscal.position'].browse(1)
        return account_position_id and account_position_id.id

    @api.multi
    def get_reinvoice_rule_ids(self):
        for txt in self.filtered(lambda x: x.partner_shipping_id != False):
            txt.rule_ids = self.env['reinvoice.rule'].get_reinvoice_rule_for_txt(txt)

    @api.multi
    def act_associate_shipping_id(self):
        for txt in self.env["invoice.txt.import"].search([('associate_id', '=', False)]):
            txt.associate_id = txt.partner_shipping_id.commercial_partner_id

    @api.multi
    def get_partner_shipping_id_from_associate_name(self):
        for txt in self.filtered(lambda x: x.associate_name and not x.partner_shipping_id):
            str = txt.associate_name
            domain = ['|', ('supplier_code', '=', str), ('supplier_str', '=', str)]
            res = self.env['res.partner'].search(domain, limit=1)
            if not res:
                domain = ['|', ('name', '=', str), ('ref', '=', str)]
                res = self.env['res.partner'].search(domain, limit=1) or False
            txt.partner_shipping_id = res or False


    def get_partner_refs(self):
        if not self.partner_vat:
            self.message_post(body='No hay NIF del proveedor')
            return
        is_message = False
        p = self.partner_vat.replace('ES', '')
        message = "<ul>"
        domain = [('supplier', '=', True), ('vat', 'ilike', '%{}%'.format(p))]
        self.partner_id = self.env['res.partner'].search(domain, limit=1)
        if not self.partner_id:
            message = "{} <li>{}</li>".format(message, 'No hay proveedor')
            is_message = True


        if self.associate_name and self.type == 'in_invoice':
            self.get_partner_shipping_id_from_associate_name()
        else:
            if self.type == 'in_refund':
                domain = ['|', ('supplier_invoice_number', '=', '{}'.format(self.original_rectificatica)), ('reference', '=', '{}'.format(self.original_rectificatica))]
                refund_inv = self.env['account.invoice'].search(domain, limit=1)
                if refund_inv:
                    self.partner_shipping_id = refund_inv.partner_id

        if not self.partner_shipping_id:
            if self.associate_name:
                message = "{} <li>{} {}</li>".format(message, 'No hay encuentro al asociado para el nombre ', self.associate_name)
            if self.original_rectificatica:
                message = "{} <li>{} {}</li>".format(message, 'No hay encuentro la factura {} para este abono', self.original_rectificatica)
            is_message = True

        message = "{}</ul>".format(message)
        if is_message:
            self.message_post(body=message)

        if self.partner_shipping_id:
            self.associate_id = self.partner_shipping_id.commercial_partner_id
            self.account_position_id = self.associate_id.property_account_position_id

        self.get_reinvoice_rule_ids()

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
            return pedido



    def get_line(self, linea_pedido, descuentos_index, cantidad_index, precio_index):

        descuento_str_total = linea_pedido[descuentos_index - 2:cantidad_index-1].strip()
        descuento = self.env['invoice.txt.import.line'].get_descuento_from_str(descuento_str_total)
        if descuento > 100:
            self.message_post(body="Error en descuento: {} obtenido de {}".format(descuento, descuento_str_total))

        codigo = linea_pedido[4:14].strip()
        num_linea = get_num(linea_pedido[0:4])
        descripcion = linea_pedido[14:82].replace(codigo, '').strip()

        tallas = linea_pedido[cantidad_index:precio_index-2].strip()
        qty = tallas.split(' ')[0]
        euros = clear_str(linea_pedido[precio_index-3:].strip()).split(' ')
        if len(euros) == 2:

            valor_neto = get_num(euros[1])
            precio_articulo = get_num(euros[0])
        if len(euros) == 1:
            valor_neto = get_num(euros[0])
            precio_articulo = valor_neto / get_num(qty)

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
        print('{}: {}€*{}uds Desc:{}% {}€'.format(clear_str(linea_pedido.strip()), qty, precio_articulo, descuento, valor_neto))
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
                    file = open(origin, 'r', encoding='latin-1',  errors="ignore")
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

        domain = [('file_name', '=', file_name)]
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
                res = txt_obj.check_adidas(str, file_name)
                if res:
                    txt_obj.create_invoice_from_invoice_txt(create_associate=True)
                return res
        return False

    def check_nike(self, str, file_name):
        return False

    def get_payment_days(self, str, line):
        find_day = False
        result = []
        inc=0
        while not find_day:
            str_strip = str[line].strip()
            date = ''
            money = ''
            if str_strip.find('Fecha vencimiento') >-1:
                line += 2
            else:
                date = get_odoo_date(str[line][36:50])
                if date:
                    money = get_num(str[line][80:100])
                line+=1
            inc += 1
            if date and money:
                result.append((date, money))
            if inc > 3 and not str_strip or inc > 7:
                find_day = True
        return result




    def check_adidas(self, str, file_name):

        print ("\nFichero de factura: {}".format(file_name))
        longitud_fichero = len(str)
        if str[1].find('ABONO') > -1:
            type = 'in_refund'
        else:
            type = 'in_invoice'
        original_rectificatica = ''
        clienteno = str[3][167:225].strip()
        facturano = str[4][167:225].strip()
        fecha_factura =  str[5][167:200]
        fecha_factura = get_odoo_date(fecha_factura)


        if type=='in_invoice':
            value_date = str[6][167:200]
            value_date = get_odoo_date(value_date)
            pay_notes = str[9][167:].strip()
        else:
            original_rectificatica = str[6][167:225].strip()
            value_date = False

        partner_nif = str[7][167:225].strip()
        pay_notes = ''
        if str[9].strip().find('Forma pago') >-1:
            pay_notes = str[9][166:220].strip()
        eori = str[10][-12:].strip()
        ###DATOS DE ALBAŔAN
        for r in range(13, 18):
            if str[r].find('Descuentos')>1:
                descuentos_index = str[r].find('Descuentos')
                cantidad_index = str[r].find('Cantidad')
                precio_index = str[r].find('Precio')

        index = 17
        supplier_picking_num = albaran = partner_bank = fecha_albaran = associate_name = region = ref_pedido = fecha_vencimiento = fecha_pedido = refund_note=False

        if type == 'in_invoice':
            if str[index].strip() and str[index].strip().find('Albar') >-1:
                albaran = str[index].split(':')[1].strip()
                if albaran:
                    datos_albaran = albaran.split()
                    supplier_picking_num = datos_albaran[0]
                    fecha_albaran = datos_albaran[1]
                    fecha_albaran = get_odoo_date(fecha_albaran)
                    index += 2
                    if str[index].strip().find('Nombre') > -1:
                        associate_name = str[index].split(':')[1].strip()
                        index += 2
                    if str[index].strip().find('Regi') > -1:
                        region = str[index].split(':')[1].strip()
                        index += 2
            else:
                self.message_post(body="No he encontrado los datos del albarán donde esperaba")
                return False
        if type == 'in_refund':
            if str[index].strip():
                self.message_post(body="Referencia del abono: {}".format(str[index].strip()))
        ### DATOS DE LAS LINEAS
        lineas=[]
        line_count = 1
        is_line = True
        index = 17
        pedido = False
        value_date = value_date or fecha_albaran or fecha_factura

        while is_line:
            if not str[index].strip():
                index += 1
                continue
            if str[index].find('Descuentos')>1:
                print ("\nEncuentro nueva linea de referencia\n {}\n".format(str[index].strip()))
                descuentos_index = str[index].find('Descuentos')
                cantidad_index = str[index].find('Cantidad')
                precio_index = str[index].find('Precio')
                index += 1
                continue
            if str[index].find('Valor neto total') > -1:
                is_line = False
                continue
            if type == 'in_invoice' and str[index].find('Su pedido no.') > -1:# str[index].split(':')[0].strip() == 'Su pedido no.':
                pedido = self.get_pedido(str[index].strip(), 'adidas')
                index += 1
                continue
            if type == 'in_refund' and line_count == 1 and not is_number_line(str[index][:4], line_count):
                refund_note = str[index].strip()
                index += 1
                continue
            if is_number_line(str[index][:4], line_count):
                linea = self.get_line(str[index], descuentos_index, cantidad_index, precio_index)
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
                continue
            index += 1

            if index >= longitud_fichero:
                self.message_post('Error leyendo las líneas del fichero')
                return False

        ## saco cuadro de factura
        inicio_impuestos = index
        inicio_payment_days = index

        def get(str, per_cent = True):
            m = get_num(str[-12:])
            m_p = 0
            if per_cent:
                end_line = str[-100:].strip().split('%')
                m_p = get_num(end_line[0])
            return m, m_p

        total = 0.00
        valor_neto = base_imponible = desc_p_p = desc_p_p_cent = iva = iva_per_cent = equiv = equiv_per_cent = recargo = igic = igic_per_cent = dua = dua_per_cent = 0

        partner_bank = ''
        while not total:
            lin = str[inicio_impuestos]

            if lin.find('Banco cliente:')>-1:
                partner_bank = get_split(str[index])[1]

            if not valor_neto and lin.find('Valor neto total') >-1:
                valor_neto, aux = get(lin, False)

            if not total and lin.find('TOTAL ABONO') >-1:
                total, aux = get(lin, False)

            if not total and lin.find('TOTAL FACTURA') >-1:
                total, aux = get(lin, False)

            if not base_imponible and lin.find('Base imponible') >-1:
                base_imponible, aux = get(lin, False)

            if not desc_p_p and lin.find('dto. pronto pago') >-1:
                desc_p_p, desc_p_p_cent = get(lin)

            if not iva and lin.find('I.V.A.')>-1:
                iva, iva_per_cent = get(lin)

            if not equiv and lin.find('R.Equiv') > -1:
                equiv, equiv_per_cent = get(lin)

            if not recargo and lin.find('recargos')>-1:
                recargo, aux = get(lin, False)

            if not igic and lin.find('I.G.I.C')>-1:
                igic, igic_per_cent= get(lin)

            if not dua and lin.find('D.U.A.')>-1:
                dua, dua_per_cent = get(lin)

            if inicio_impuestos >= longitud_fichero:
                self.message_post('Error leyendo el total de la factura')
                return False
            inicio_impuestos += 1
        payment_days = self.get_payment_days(str, inicio_payment_days)
        pedido = self.order_ids and self.order_ids[0]

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
            'supplier_order_num': pedido.name,
            'supplier_order_date':  pedido.fecha,
            'partner_bank': partner_bank,
            'recargos': recargo,
            'state': 'draft',
            'desc_p_p': desc_p_p,
            'desc_p_p_per_cent': desc_p_p_cent,
            'iva_per_cent': iva_per_cent,
            'iva': iva,
            'equiv_per_cent': equiv_per_cent,
            'equiv': equiv,
            'igic': igic,
            'igic_per_cent': igic_per_cent,
            'dua': dua,
            'dua_per_cent': dua_per_cent,
            'fecha_vencimiento': payment_days and payment_days[len(payment_days)-1][0],
            'value_date': value_date or fecha_albaran,
            'num_lineas': line_count,
            'total_amount': total,
            'type': type,
            'refund_note': refund_note,
            'original_rectificatica':original_rectificatica,
            'payment_days': payment_days,

        }
        self.write_invoice_from_txt(txt_invoice_val, lineas)
        for day in payment_days:
            self.env['payment.day.txt'].create({'txt_id': self.id, 'date': day[0], 'amount': day[1]})
        self.date_due = self.payment_day_ids and self.payment_day_ids[0].date or self.value_date
        if not self:
            self.message_post(body="error al escribir los valores en el invoice txt")
            return False
        if not self.partner_id:
            self.message_post(body="No se ha encontrado un partner")
            return False
        else:
            return True

        return True

    def write_invoice_from_txt(self, txt_invoice_val, lineas):
        self.write(txt_invoice_val)
        if not self.partner_shipping_id:
            self.get_partner_refs()
        self.invoice_line_txt_import_ids.unlink()
        for linea in lineas:
            product_id = self.get_product(linea, self.partner_id.id)
            linea.update(invoice_txt_import_id=self.id,
                         product_id = product_id and product_id.id)
            self.env['invoice.txt.import.line'].create(linea)
        return True

    @api.multi
    def delete_invoice_from_txt(self):
        for txt in self.filtered(lambda x:x.invoice_id):
            if txt.invoice_id.customer_invoice_id:
                try:
                    txt.invoice_id.customer_invoice_id.unlink()
                except Exception:
                    pass
            try:
                txt.invoice_id.unlink()
            except Exception:
                pass
            txt.state='draft'



    @api.multi
    def create_invoice_from_invoice_txt(self, create_associate=False):
        new_invoice_ids = self.env['account.invoice']
        for txt in self:
            txt.state = 'invoiced'
            txt_message = '<ul>'
            inv_message = '<ul>'
            txt.get_partner_refs()
            refund_invoice_id = False
            payment_term_id = False
            create_inv = True
            if not txt.partner_id:
                txt_message ='{} <li>{}</li>'.format(txt_message, "No encuentro proveedor")
                create_inv=False
            if not txt.associate_id or not txt.partner_shipping_id:
                txt_message = '{} <li>{}</li>'.format(txt_message, "No encuentro asociado")
                create_inv = False
            if txt.pay_notes:
                payment_term_id = self.env['account.payment.term'].search([('name', '=', txt.pay_notes)], limit=1)
                if not payment_term_id and txt.partner_id:
                    term_domain = [('supplier_id', '=', txt.partner_id.id), ('name', '=', txt.pay_notes)]
                    payment_term_brand_id = self.env['payment.term.brand.name'].search(term_domain,limit=1)
                    if payment_term_brand_id:
                        payment_term_id = payment_term_brand_id.payment_term_id
                if not payment_term_id:
                    payment_term_id = txt.partner_id.property_supplier_payment_term_id
                    txt_message = '{} <li>{}</li>'.format(txt_message,"Se aplica el plazo de pago del proveedor")
                    inv_message = '{} <li>{}</li>'.format(inv_message, "Se aplica el plazo de pago del proveedor")
                if txt.pay_notes and not payment_term_id:
                    txt_message = '{} <li>{}</li>'.format(txt_message, "No se ha encontrado un plazo de pago para %s y no se encuentra un plazo en el proveedor"%txt.pay_notes)
                    inv_message = '{} <li>{}</li>'.format(inv_message, "No se ha encontrado un plazo de pago para %s y no se encuentra un plazo en el proveedor"%txt.pay_notes)


            if self.type == 'in_refund':
                comment = 'Corresponde a la factura rectificativa nº {}, de fecha: {}. Factura original: {}'.format(txt.supplier_invoice_num,
                                                                      txt.supplier_invoice_date, txt.original_rectificatica)

                refund_invoice_id = self.env['account.invoice'].search([('reference', '=', txt.original_rectificatica)])
                if refund_invoice_id:
                    txt.partner_shipping_id = refund_invoice_id.associate_id
                    txt.associate_name = refund_invoice_id.associate_id.name
                else:
                    message = "No encuentro la factura original {} para esta rectificativa".format(txt.original_rectificatica)
                    txt_message = '{} <li>{}</li>'.format(txt_message, message)
                    inv_message = '{} <li>{}</li>'.format(inv_message, message)
            else:
                comment = "Corresponde a la factura de {}, nº {}, de fecha: {}. Albarán nº: {}".format(
                                                                      txt.partner_id.name,
                                                                      txt.supplier_invoice_num,
                                                                      txt.supplier_invoice_date,
                                                                      txt.supplier_picking_num)
            currency_id = txt.associate_id.property_product_pricelist.currency_id and txt.associate_id.property_product_pricelist.currency_id.id or txt.partner_id.property_product_pricelist.currency_id.id

            same_supplier_inv_num = self.env['account.invoice'].search([
                ('commercial_partner_id', '=', txt.partner_id.commercial_partner_id.id),
                ('type', 'in', ('in_invoice', 'in_refund')),
                ('supplier_invoice_number', '=', txt.supplier_invoice_num),
            ], limit=1)
            if same_supplier_inv_num:
                create_inv = False
                message ="Se ha encontrado una factura para este numero de factura de proveedor"
                txt_message = '{} <li>{}</li>'.format(txt_message, message)
                txt.invoice_id = same_supplier_inv_num

            if not currency_id:
                create_inv = False
                message ="No encuentro moneda"
                txt_message = '{} <li>{}</li>'.format(txt_message, message)
            journal_id = txt.env['account.journal'].search([('name', '=', 'Refacturas')])
            if not journal_id:
                create_inv = False
                message ="No encuentro diario de refacturas"
                txt_message = '{} <li>{}</li>'.format(txt_message, message)

            if not txt.account_position_id:
                txt.account_position_id = txt.partner_shipping_id.commercial_partner_id.property_account_position_id

            if not txt.account_position_id:
                create_inv = False
                message = "No posición fiscal para el asociado {}".format(txt.partner_shipping_id and txt.partner_shipping_id.display_name or "Sin asociado")
                txt_message = '{} <li>{}</li>'.format(txt_message, message)

            if not create_inv:
                txt_message = "</ul>{}".format(txt_message, "Este fichero no ha generado la factura")
                txt.message_post(body=txt_message)
                txt.state = 'error'
                continue
            sale_type_id = txt.mapped('partner_shipping_id').mapped('sale_type') or  txt.mapped('associate_id').mapped('sale_type')

            invoice_val = {
                'type': self.type or 'in_invoice',
                'partner_shipping_id': txt.partner_shipping_id.id,
                'associate_id': txt.associate_id.id,
                'associate_shipping_id': txt.partner_shipping_id.id,
                'partner_id': txt.partner_id.id,
                'supplier_invoice_number': txt.supplier_invoice_num,
                'reference': txt.supplier_invoice_num,
                'currency_id': currency_id,
                'journal_id': journal_id and journal_id[0].id or False,
                'date_invoice': txt.supplier_invoice_date,
                'date_due': txt.fecha_vencimiento,
                'company_id': 1,
                'operating_unit_id': journal_id.operating_unit_id.id,
                'check_total': txt.total_amount,
                'refund_invoice_id': refund_invoice_id,
                'payment_term_id': payment_term_id and payment_term_id.id,
                'name': txt.supplier_invoice_num,
                'origin': txt.supplier_picking_num,
                'comment': comment,
                'value_date': txt.value_date,
                'import_txt_id': txt.id
            }

            ## TODO NO ENTIENDO ESTO
            invoice = self.env['account.invoice'].new(invoice_val)
            invoice._onchange_partner_id()
            inv = invoice._convert_to_write(invoice._cache)
            inv.update(journal_id=journal_id.id,
                       fiscal_position_id=self.map_account_possition(txt.account_position_id),
                       payment_term_id=payment_term_id and payment_term_id.id or 1)

            if not inv.get('operating_unit_id', False) and sale_type_id:
                inv.update(operating_unit_id=sale_type_id.operating_unit_id and sale_type_id.operating_unit_id.id)

            new_invoice = self.env['account.invoice'].create(inv)
            new_invoice.journal_id = journal_id
            new_invoice.date_due = txt.fecha_vencimiento
            txt.invoice_id = new_invoice
            for linea in txt.invoice_line_txt_import_ids:
                vals = linea.get_line_vals(new_invoice.id)
                invoice_line = self.env['account.invoice.line'].new(vals)
                invoice_line._onchange_product_id()
                invoice_line.invoice_line_tax_ids = new_invoice.fiscal_position_id.map_tax(
                    invoice_line.invoice_line_tax_ids, invoice_line.product_id, new_invoice.associate_id)
                inv_line = invoice_line._convert_to_write(invoice_line._cache)
                inv_line.update(name=vals['name'], price_unit=linea['precio_articulo'], discount=linea['descuento'])
                self.env['account.invoice.line'].create(inv_line)
            new_invoice.compute_taxes()
            txt.check_txt_amount_total(new_invoice)

            print("\n------------\nFACTURA PARA : {}\n------------\n".format(new_invoice.partner_shipping_id.name or self.partner_id.name))

            inv_message = "{}</ul>{}".format(inv_message, "Esta factura ha sido creada desde el fichero: <a href=# data-oe-model=invoice.txt.import data-oe-id=%d>%s</a>"% (txt.id, txt.file_name))
            new_invoice.message_post(body=inv_message)
            txt_message = "{}</ul>{}".format(txt_message,
                                     "Este fichero ha generado la factura: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>" % (
                                     new_invoice.id, new_invoice.name))

            txt.message_post(body=txt_message)
            new_invoice_ids += new_invoice

        #if create_associate:
            new_invoice_ids.filtered(lambda x: x.associate_id).do_reinvoice()
        return new_invoice_ids.ids


    @api.multi
    def unlink(self):
        try:
            self.mapped('invoice_id').filtered(lambda x
                                           :x.state=='draft').unlink()
        except Exception:
            pass
        return super().unlink()



    def check_txt_amount_total(self, invoice):

        iat = round(invoice.amount_total, 2)
        tat = round(self.total_amount, 2)
        price = round(tat - iat,2)
        if iat != tat:
            if invoice.amount_tax and invoice.tax_line_ids and abs(iat-tat) <= 1.00:
                new_tax = round(invoice.tax_line_ids[0].amount_total + price, 2)
                invoice.tax_line_ids[0].amount = new_tax
                message = "Cambio impuestos de {} a {}".format(invoice.tax_line_ids[0].amount_total, new_tax)
            else:
                product_id = self.env['product.product'].search([('default_code', '=', 'REDONDEO.000')], limit=1)
                vals = {'product_id': product_id and product_id.id,
                    'quantity': 1,
                    'price_unit': price,
                    'discount': 0,
                    'name': 'AJUSTE REDONDEO',
                    'imported_price_subtotal': 0.00,
                    'invoice_id': invoice.id}

                invoice_line = self.env['account.invoice.line'].new(vals)
                invoice_line._onchange_product_id()
                invoice_line.invoice_line_tax_ids = invoice.fiscal_position_id.map_tax(
                    invoice_line.invoice_line_tax_ids, invoice_line.product_id, invoice.associate_id)
                inv_line = invoice_line._convert_to_write(invoice_line._cache)
                inv_line.update(name='AJUSTE REDONDEO', price_unit=price, discount=0.00)
                self.env['account.invoice.line'].create(inv_line)
                message = "Añado línea de redondeo por valor {}".format(price)
            self.message_post(message)
        return