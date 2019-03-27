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

from odoo import models, fields, config
from odoo.exceptions import UserError
from mimetypes import guess_type
from hashlib import sha1

_logger = logging.getLogger(__name__)

FOLDERINPUT='/opt/hotfolder/images/'
SPLITER = re.compile(r'(.*?)(?:_(\d*))?(?:\.(?:\w+))$')
CODECOLOR = re.compile(r'^([a-z0-9]+)(?:[\,-_ ](\w+))?',re.IGNORECASE)

class ImportImagesValue():
    """ mimic ir.attachment 
    TODO:
        Variables a metodos
        ??? api.multi y pasarlo a transient modeil heredando ir.attachment
    """

    name ='image' 
    res_model = 'product.template'
    res_id = None
    type = 'binary'
    checksum = None

    def __init__(self, filepath):
        self.filepath = filepath
        self.res_name = self.basename()
        self.reference, self.order = SPLITER.match(self.basename()).groups()
        self.order = self.order or 0

    def res_field(self):
        return self.name

    def file_size(self):
        return os.path.getsize(self.filepath)

    def __checksum(self):
        with open(self.filepath,'rb') as f:
            self.checksum = sha1(f.read()).hexdigest()

    def mimetype(self):
        return guess_type(self.filepath)[0]

    def basename(self):
        return os.path.basename(self.filepath)

    def store_fname(self):
        pass

    def copy(self,size=None):
        if size == 'small':
            pass
        elif size == 'medium':
            pass
        else:
            pass

    def __repr__(self):
        return dict(
                name=self.name,
                res_name=self.res_name,
                res_model=self.res_model,
                res_field=self.res_field(),
                res_id = self.res_id,
                type=self.type,
                file_size=self.file_size(),
                checksum=self.checksum(),
                store_fname=self.store_fname(),
                mimetype=self.mimetype())
    # TODO expand image tipes

class ImportImages(models.TransientModel):
    """
        Transient model for import images
        TODO:
            Reemplazar el boton de importar
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
            if os.access(file,os.R_OK,os.W_OK)
                image = ImportImagesValue(file)
                imported.append(image)
            
        imported = sorted(imported, key=lambda image: image.basename)

        ref = ''
        groups = []
        for image in imported:
            if ref != image.basename():
                ref = image.basename()
                groups.append([])
            groups[-1].append(image)

        rem = []
        for ind, references in enumerate(groups):
            table = 'product.product'
            code, color = CODECOLOR.match(references[0].basename).groups()
            domain = [('default_code','ilike',code+'%' if not color else '_'+color+'%')]
            if not color and re.match(r'\d{12,14}',code):
                domain = [('barcode','=',code)]
            tmpl_ids = self.env[table].read_group(domain,('product_tmpl_id'),('product_tmpl_id'))['product_tmpl_id']
            pdb.set_trace()
            if not len(tmpl_ids) == 1:
                # ??? log
                rem.append(ind)
            else:
                for image in references:
                    image.res_id = tmpl_ids[0]

        for i in rem:
            groups.pop(i)
        
        return groups

    def action_import_images(self):
        images = self._get_images()
        pdb.set_trace()
        pass
