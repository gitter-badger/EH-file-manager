# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys
import hashlib

from database_model import DatabaseModel

class GalleryManager():
    """
    Main class of application
    """
    
    def __init__(self, gallerypath=None, configdir='.config'):
        self.gallerypath = gallerypath
        self.configdir = configdir
        self.dbmodel = None
        
        if self.gallerypath is not None:
            self.open_path(self.gallerypath)
            
    def close(self):
        """
        Closes connection to gallery.
        """
        self.dbmodel.close_database()
    
    def open_path(self, path):
        """
        Open path as a gallery and creates connection to its database. If path is not gallery creates empty gallery structure.
        """
        self.gallerypath = path
        # checks if path is existing gallery. if not creates one.
        if self.is_gallery(self.gallerypath) is False:
            self.init_gallery(self.gallerypath)
            
        # open connection to database
        self.dbmodel = DatabaseModel(self.gallerypath, configdir=self.configdir)
        self.dbmodel.open_database()   
    
    # TODO - propper check
    def is_gallery(self, path):
        """
        Checks if path leads to existing gallery.
        """
        if os.path.isdir(os.path.join(path, self.configdir)) is True:
            logger.debug('is_gallery: given path is existing gallery.')
            return True
        else:
            logger.debug('is_gallery: given path is not gallery.')
            return False
        
    def init_gallery(self, path, destructive=False):
        """
        Creates new gallery basic structure.
        """
        logger.debug('Creating new gallery structure...')
        
        # create folder structure
        os.mkdir(os.path.join(path, self.configdir))
        os.mkdir(os.path.join(path, "Files"))
        
    def get_filehash(self, filepath):
        """
        Returns file MD5 hash.
        """
        
        afile = open(filepath, 'rb')
        buf = afile.read()
        afile.close()
        
        hasher = hashlib.md5()
        hasher.update(buf)
        
        md5hash = hasher.hexdigest()
        logger.debug('Generated md5 hash - '+str(md5hash))
        
        return md5hash
        
    def process_file(self, filepath):
        logger.debug('Processing file - '+str(filepath))
        md5hash = self.get_filehash(filepath)
        filename = os.path.basename(filepath)
        
        self.dbmodel.add_file(md5hash, filename, names={'eng':os.path.splitext(filename)[0],'jp':''})
        
    # TODO - not needed in end product
    def get_file_info(self, filepath):
        md5hash = self.get_filehash(filepath)
        info = self.dbmodel.get_files_by_hash(md5hash)
        
        return info
        
    def update_file(self, filehash):
        pass
