# -*- coding: utf-8 -*-

"""
    Import images

    TODO:
        Un segundo modelos con el resultado
        Ampliar fuentes, opciones:
            - ??? FTP
            - ??? URL
        os.walk(..., onerror=func)
        con el ean escoger product.product no solo template
        refactorizar los bucles
"""

import os
import logging
import pdb
import re

from odoo import models, fields
from odoo.exceptions import UserError
from mimetypes import guess_type
from base64 import b64encode
from hashlib import sha1

_logger = logging.getLogger(__name__)

FOLDERINPUT='/opt/hotfolder/images/'
SPLITER = re.compile(r'(.*?)(?:_(\d*))?(?:\.(?:\w+))$')
CODECOLOR = re.compile(r'^([a-z0-9]+)(?:[\,-_ ](\w+))?',re.IGNORECASE)

def coroutine(func):
    def start(*args,**kwargs)
        cr = func(*args, **kwargs):
        cr.next()
        return cr
    return start

def listfiles(path, recursive=False):
        """ Generator """
        root, dirs, files = next(os.walk(self.folder))
        for file in files:
            yield os.path.join(root, file)
        if recursive:
            for dir in dirs:
                yield from listfiles(os.path.join(root, dir))

@coroutine
def file_filter_access(perm = os.R_OK & os.W_OK):
    try:
        while True:
            file = (yield)
            if os.access(file,perm):
                image = ImportImagesValue(file)
                imported.append(image)
    except GeneratorExit: # handle Close
        pass
        # Done
    

class ImportImagesValue():
    """  
    TODO:
        Model.Transient with results
        New Model that:
            Inherit IrAttachment and implement new engines (URL, S3 etc)
            https://github.com/antibios/odoo-s3/blob/master/models/models.py
            https://github.com/maxmumford/oe_import_product_images/blob/master/import_product_images.py
    """

    name ='image' 
    res_id = None
    type = 'binary'
    index_content = "image"
    _data = None
    _checksum = None

    def __init__(self, filepath):
        self.filepath = filepath
        self.res_name = self.basename()
        self.reference, self.order = SPLITER.match(self.basename()).groups()
        self.order = int(self.order) if  self.order else 0

    def res_field(self):
        return self.name

    def file_size(self):
        return os.path.getsize(self.filepath)

    def mimetype(self):
        return guess_type(self.filepath)[0]

    def basename(self):
        return os.path.basename(self.filepath)

    def data(self):
        if not self._data:
            with open(self.filepath, 'r+b') as f:
                self._data = b64encode(f.read())
        return self._data

    def dump(self):
        return {'image':self.data(), 'image_medium':self.data(), 'image_small':self.data()}

    def checksum(self):
        """ TODO: mimic decorator api.depend? """
        if not self._checksum:
            self._checksum = sha1(self.data()).hexdigest()
        return self._checksum

    def attachment(self, res_id,res_name=None):
        """ """
        return dict(name="image",
                res_name = res_name or self.res_name,
                res_model= 'product.image',
                res_field= 'image',
                res_id   = res_id,
                type     = 'binary',
                datas    = self.data())


class ImportImages(models.TransientModel):
    """
        Transient model for import images
        TODO:
            Reemplazar el boton de importar
            _get_filters as coroutines
            if folder imput == FTP:// get conection
    """

    _name = 'import.images'
    
    folder = fields.Char('Folder input', required=True, default=FOLDERINPUT)
    recursive = fields.Boolean('Recursive search', default=False)
    update_default = fields.Boolean('Update default image', default=False)

    def _get_files(self):
        """ """
        root, dirs, files = next(os.walk(self.folder))
        for file in files:
            yield os.path.join(root, file)
        if self.recursive:
            for dir in dirs:
                yield from get_files(os.path.join(root, dir))
    
    def _get_file_images(self):
        """ """
        for file in self._get_files():
            type = guess_type(file)
            if type and type[0].split('/')[0] == 'image':
                yield file
    
    # TODO filter for valid types

    def _get_images(self):
        """ Notes:
                Por claridad vamos a separar los bucles
        """
        imported = []
        for file in self._get_file_images():
            if os.access(file,os.R_OK & os.W_OK):
                image = ImportImagesValue(file)
                imported.append(image)
            
        imported = sorted(imported, key=lambda image: image.reference)

        ref = ''
        groups = []
        for image in imported:
            if ref != image.reference.lower():
                ref = image.reference.lower()
                groups.append([])
            groups[-1].append(image)

        rem = []
        for ind, references in enumerate(groups):
            table = 'product.product'
            code, color = CODECOLOR.match(references[0].reference).groups()
            domain = [('default_code','=ilike',code+'%' if not color else code+'_'+color+'%')]
            if not color and re.match(r'\d{12,14}',code):
                domain = [('barcode','=',code)]
            tmpl_ids = self.env[table].read_group(domain,['product_tmpl_id'],['product_tmpl_id'])
            if not len(tmpl_ids) == 1:
                rem.append(ind)
            else:
                for image in references:
                    image.res_id = tmpl_ids[0]['product_tmpl_id'][0]

        groups = [val for ind, val in enumerate(groups) if ind not in rem]
        
        return groups

    def action_import_images(self):
        """ """
        gimages = self._get_images()
        for images in gimages:
            images = sorted(images, key=lambda image: image.order)
            templ = self.env['product.template'].search([('id','=',images[0].res_id)])
            once = False
            for image in images:
                if not templ.image:
                    once = True
                    templ.write(image.dump())
                    continue
                elif not once and self.update_default:
                    once = True
                    templ.write(image.dump())
                    continue
                if not len(self.env['ir.attachment'].search([('checksum','=',image.checksum()),('res_id','=',templ.id)])._ids):
                    templ_image = self.env['product.image'].create({'name':templ.name,'product_tmpl_id':templ.id})
                    self.env['ir.attachment'].create(image.attachment(templ_image.id, templ.name))
