#!/usr/bin/env python3

import sys
import xmlrpc.client
import socket

class SetStateIdFromZip(object):
    def __init__(self, dbname, user, passwd, port):
        """método incial"""

        try:
            self.url_template = "http://%s:%s/xmlrpc/%s"
            self.server = "localhost"
            self.port = int(port)
            self.dbname = dbname
            self.user_name = user
            self.user_passwd = passwd

            #
            # Conectamos con OpenERP
            #
            login_facade = xmlrpc.client.ServerProxy(self.url_template % (self.server, self.port, 'common'))
            self.user_id = login_facade.login(self.dbname, self.user_name, self.user_passwd)
            self.object_facade = xmlrpc.client.ServerProxy(self.url_template % (self.server, self.port, 'object'))

            res = self.set_state_id()
            #con exito
            if res:
                print("All set")
        except Exception as e:
            print("ERROR: ", e)
            sys.exit(1)

        #Métodos Xml-rpc

    def exception_handler(self, exception):
        """Manejador de Excepciones"""
        print("HANDLER: ", exception)
        return True

    def create(self, model, data, context={}):
        """
        Wrapper del metodo create.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                                            model, 'create', data, context)
            return res
        except socket.error as err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception(u'Error %s en create: %s' % (err.faultCode, err.faultString))


    def search(self, model, query, offset=0, limit=False, order=False, context={}, count=False, obj=1):
        """
        Wrapper del metodo search.
        """
        try:
            ids = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'search', query, offset, limit, order, context, count)
            return ids
        except socket.error as err:
                raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
                raise Exception(u'Error %s en search: %s' % (err.faultCode, err.faultString))


    def read(self, model, ids, fields, context={}):
        """
        Wrapper del metodo read.
        """
        try:
            data = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                            model, 'read', ids, fields, context)
            return data
        except socket.error as err:
                raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
                raise Exception(u'Error %s en read: %s' % (err.faultCode, err.faultString))


    def write(self, model, ids, field_values,context={}):
        """
        Wrapper del metodo write.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                                    model, 'write', ids, field_values, context)
            return res
        except socket.error as err:
                raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
                raise Exception(u'Error %s en write: %s' % (err.faultCode, err.faultString))


    def unlink(self, model, ids, context={}):
        """
        Wrapper del metodo unlink.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                                    model, 'unlink', ids, context)
            return res
        except socket.error as err:
                raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
                    raise Exception(u'Error %s en unlink: %s' % (err.faultCode, err.faultString))

    def default_get(self, model, fields_list=[], context={}):
        """
        Wrapper del metodo default_get.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                        model, 'default_get', fields_list, context)
            return res
        except socket.error as err:
                raise Exception('Conexion rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
                raise Exception('Error %s en default_get: %s' % (err.faultCode, err.faultString))

    def execute(self, model, method, *args, **kw):
        """
        Wrapper del método execute.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                                                model, method, *args, **kw)
            return res
        except socket.error as err:
                raise Exception('Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
                raise Exception('Error %s en execute: %s' % (err.faultCode, err.faultString))

    def exec_workflow(self, model, signal, ids):
        """ejecuta un workflow por xml rpc"""
        try:
            res = self.object_facade.exec_workflow(self.dbname, self.user_id, self.user_passwd, model, signal, ids)
            return res
        except socket.error as err:
            raise Exception(u'Conexión rechazada: %s!' % err)
        except xmlrpc.client.Fault as err:
            raise Exception(u'Error %s en exec_workflow: %s' % (err.faultCode, err.faultString))


    def set_state_id(self):
        partner_b2c_ids = self.search('res.partner', [('zip', '!=', False)])
        partner_b2b_ids = self.search('res.partner', [('street2', '!=', False),('zip', '=', False)])
        count_b2c = len(partner_b2c_ids)
        count_b2b = len(partner_b2b_ids)
        print("partners b2c no: ", count_b2c)
        cont = 1
        cont2 = 1

        for partner_data in self.read("res.partner", partner_b2c_ids, ['name', 'zip']):
            try:
                partner_id = partner_data['id']
                zip_ids = self.search("res.better.zip", [('name', '=', partner_data['zip']),('country_id.code', '=', 'ES')], limit=1)
                if zip_ids:
                    zip_read = self.read("res.better.zip", zip_ids[0], ['state_id', 'country_id'])
                    self.write("res.partner", [partner_id], {'state_id': zip_read[0]['state_id'],
                                                             'country_id': zip_read[0]['country_id']})
                print(cont, " de ", count_b2c)
                cont += 1
            except Exception as e:
                print("EXCEPTION: ", e, " Part: ", partner_data['name'])

        print("partners partner_b2b_ids no: ", count_b2b)
        for partner_data in self.read("res.partner", partner_b2b_ids, ['name', 'street2']):
            try:
                partner_id = partner_data['id']
                zipcode = partner_data['street2'].split()
                if zipcode[0].isdigit():
                    zip_ids = self.search("res.better.zip", [('name', '=', zipcode[0]),('country_id.code', '=', 'ES')], limit=1)
                    if zip_ids:
                        zip_read = self.read("res.better.zip", zip_ids[0], ['state_id', 'country_id'])
                        self.write("res.partner", [partner_id], {'state_id': zip_read[0]['state_id'],
                                                                 'country_id': zip_read[0]['country_id'],
                                                                 'zip': zipcode[0]})
                print(cont2, " de ", count_b2b)
                cont2 += 1
            except Exception as e:
                print("EXCEPTION: ", e, " Part: ", partner_data['name'])

        return True


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: ", sys.argv[0], "<dbname> <user> <password> <port>")
    else:
        SetStateIdFromZip(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
