# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys
import hashlib

import requests
import json

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
        
    def info_from_ehentai_link(self, ehlink):
        """
        Returns ehentai.org gallery metdata from gallery link.
        """
        index = ehlink.find('hentai.org/g/')
        splited = ehlink[(index+13):].split('/')
        
        gallery_id = splited[0]
        gallery_token = splited[1]
        
        return self.info_from_ehentai(gallery_id, gallery_token)
    
    def info_from_ehentai(self, gallery_id, gallery_token):
        """
        Returns ehentai.org gallery metadata from gallery_id and gallery_token.
        http://ehwiki.org/wiki/API
        """
        payload = json.dumps({'method': 'gdata', 'gidlist': [[gallery_id, gallery_token]]})
        headers = {'content-type': 'application/json'}
        
        r = requests.post("http://g.e-hentai.org/api.php", data=payload, headers=headers)
        gallery_info = r.json()['gmetadata'][0]
        
        return gallery_info 
    
    def get_filehash(self, filepath):
        """
        Returns MD5 hash of file.
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
        """
        Add file to database
        """
        logger.debug('Processing file - '+str(filepath))
        md5hash = self.get_filehash(filepath)
        filename = os.path.basename(filepath)
        names = {'eng':os.path.splitext(filename)[0],'jp':''}
        
        self.dbmodel.add_file(md5hash, filename, names=names)
        
    # TODO - not needed in end product
    def get_file_info(self, filepath):
        md5hash = self.get_filehash(filepath)
        return self.get_file_by_hash(md5hash)
        
    def get_file_by_hash(self, filehash):
        """
        Returns fileinfo
        """
        info = self.dbmodel.get_files_by_hash(filehash)
        return info
    
    # TODO - finish this
    def search(self, searchstring):
        """
        Returns filtered list of files
        """
        searchstring = searchstring.lower()
        all_files = self.dbmodel.get_files()
        
        filtered = []
        for f in all_files:
            title = f[2].lower()
            title_jpn = f[3].lower()
            category = f[4].lower()
            tags = [w.replace('_',' ').lower() for w in f[5].split(' ')]         
            
            eq = False
            if searchstring == title:
                eq = True
            if searchstring == title_jpn:
                eq = True
            if searchstring == category:
                eq = True
            if searchstring in tags:
                eq = True
                
            if eq == True:
                filtered.append(f)
                        
        return filtered
        
        
        
        
