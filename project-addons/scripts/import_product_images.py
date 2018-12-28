#!/usr/bin/env python3

import sys
import xmlrpc.client
import socket
import glob
import os
import base64
import io
from os.path import join
import xlrd

class DatabaseImport:
    """
    Importa a OpenERP datos de una base de datos SqlServer para Calor Color.
    """

    def __init__(self, dbname, user, passwd, port, xls_file, image_path):
        """
        Inicializar las opciones por defecto y conectar con OpenERP
        """


    #-------------------------------------------------------------------------
    #--- WRAPPER XMLRPC OPENERP ----------------------------------------------
    #-------------------------------------------------------------------------


        self.url_template = "http://%s:%s/xmlrpc/2/%s"
        self.server = "localhost"
        self.port = int(port)
        self.dbname = dbname
        self.user_name = user
        self.user_passwd = passwd
        self.user_id = 0
        self.path = image_path
        self.xls_file = xls_file

        #
        # Conectamos con OpenERP
        #
        login_facade = xmlrpc.client.ServerProxy(self.url_template % (self.server, self.port, 'common'))
        self.user_id = login_facade.login(self.dbname, self.user_name, self.user_passwd)
        self.object_facade = xmlrpc.client.ServerProxy(self.url_template % (self.server, self.port, 'object'))

        #
        # Fichero Log de Excepciones
        #
        self.file = open("importation_log.txt", "w")

    def exception_handler(self, exception):
        """Manejador de Excepciones"""
        print("HANDLER: ", exception)
        self.file.write("WARNING: %s\n\n\n" % repr(exception))
        return True

    def create(self, model, data, context={}):
        """
        Wrapper del método create.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                model, 'create', data, context)

            if isinstance(res, list):
                res = res[0]

            return res
        except socket.error as err:
            raise Exception(u'Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception(u'Error %s en create: %s' % (err.faultCode, err.faultString))

    def exec_workflow(self, model, signal, ids):
        """ejecuta un workflow por xml rpc"""
        try:
            res = self.object_facade.exec_workflow(self.dbname, self.user_id, self.user_passwd, model, signal, ids)
            return res
        except socket.error as err:
            raise Exception(u'Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception(u'Error %s en exec_workflow: %s' % (err.faultCode, err.faultString))

    def search(self, model, query, context={}):
        """
        Wrapper del método search.
        """
        try:
            ids = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                model, 'search', query, context)
            return ids
        except socket.error as err:
            raise Exception(u'Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception(u'Error %s en search: %s' % (err.faultCode, err.faultString))


    def read(self, model, ids, fields, context={}):
        """
        Wrapper del método read.
        """
        try:
            data = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'read', ids, fields, context)
            return data
        except socket.error as err:
            raise Exception(u'Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception(u'Error %s en read: %s' % (err.faultCode, err.faultString))


    def write(self, model, ids, field_values, context={}):
        """
        Wrapper del método write.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'write', ids, field_values, context)
            return res
        except socket.error as err:
            raise Exception(u'Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception(u'Error %s en write: %s' % (err.faultCode, err.faultString))


    def unlink(self, model, ids, context={}):
        """
        Wrapper del método unlink.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'unlink', ids, context)
            return res
        except socket.error as err:
            raise Exception(u'Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception(u'Error %s en unlink: %s' % (err.faultCode, err.faultString))

    def default_get(self, model, fields_list=[], context={}):
        """
        Wrapper del método default_get.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'default_get', fields_list, context)
            return res
        except socket.error as err:
            raise Exception('Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception('Error %s en default_get: %s' % (err.faultCode, err.faultString))

    def execute(self, model, method, ids, context={}):
        """
        Wrapper del método execute.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, method, ids, context)
            return res
        except socket.error as err:
            raise Exception('Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception('Error %s en execute: %s' % (err.faultCode, err.faultString))

    def insert_image(self, product_id, fname):
        with open(join(self.path, fname), "rb") as f:
            data = f.read()
            self.write("product.product", product_id, {'image_medium': base64.encodestring(data).decode()})

    def insert_extra_image(self, product_data, fname):
        with open(join(self.path, fname), "rb") as f:
            data = f.read()
            self.create("product.image", {'product_tmpl_id': product_data[0]['product_tmpl_id'],
                                          'name': fname,
                                          'image': base64.encodestring(data).decode()})

    def import_product_image(self):
        cwb = xlrd.open_workbook(self.xls_file, encoding_override="utf-8")
        sh = cwb.sheet_by_index(0)

        cont = 1
        all_lines = sh.nrows - 1
        print("Numero de lineas: ", all_lines)
        os.chdir(self.path)
        for rownum in range(1, all_lines):
            record = sh.row_values(rownum)
            if record[3]:
                arr = sorted(glob.glob(record[3] + '*.jpg'))
                image_set = False
                for filename in arr:
                    try:
                        print("filename: ", filename)
                        product_id = self.search("product.product", [('default_code', '=', record[0])])
                        if product_id:
                            product_data = self.read('product.product', product_id[0], ['product_tmpl_id'])
                            if not image_set:
                                self.insert_image(product_id[0], filename)
                                image_set = True
                            else:
                                self.insert_extra_image(product_data, filename)
                    except Exception as e:
                        print("Exception: ", e)

            cont += 1
            print(cont, " de ", all_lines)

    def process_data(self):
        """
        Importa la bbdd
        """
        try:
            self.import_product_image()

        except Exception as ex:
            print("Error: ", ex)
            sys.exit()

        self.file.write(u"Iniciamos la Importacion\n\n")


        #cerramos el fichero
        self.file.close()

        return True

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Uso: ",  sys.argv[0], " <dbname> <user> <password> <port> <xls_file> <image_path>")
    else:
        ENGINE = DatabaseImport(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

        ENGINE.process_data()
