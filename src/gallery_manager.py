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
            self.openPath(self.gallerypath)
            
    def close(self):
        """
        Closes connection to gallery.
        """
        self.dbmodel.closeDatabase()
    
    def openPath(self, path):
        """
        Open path as a gallery and creates connection to its database. If path is not gallery creates empty gallery structure.
        """
        self.gallerypath = os.path.abspath(path)
        # checks if path is existing gallery. if not creates one.
        if self.isGallery(self.gallerypath) is False:
            self.initGallery(self.gallerypath)
            
        # open connection to database
        self.dbmodel = DatabaseModel(self.gallerypath, configdir=self.configdir)
        self.dbmodel.openDatabase()   
    
    # TODO - propper check
    def isGallery(self, path):
        """
        Checks if path leads to existing gallery.
        """
        if os.path.isdir(os.path.join(path, self.configdir)) is True:
            logger.debug('isGallery: given path is existing gallery.')
            return True
        else:
            logger.debug('isGallery: given path is not gallery.')
            return False
        
    def initGallery(self, path, destructive=False):
        """
        Creates new gallery basic structure.
        """
        logger.debug('Creating new gallery structure...')
        
        # create folder structure
        os.mkdir(os.path.join(path, self.configdir))
    
    def getHash(self, filepath):
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
        
    def addFile(self, filepath):
        """
        Add fileinfo to database
        """
        logger.debug('Processing file - '+str(filepath))
        md5hash = self.getHash(filepath)
        
        # get relative filepath to gallery path
        commonprefix = os.path.commonprefix([self.gallerypath, filepath])
        if commonprefix != self.gallerypath:
            logger.error('File is not in child directory of gallery!!!'+ \
                        '\nfilepath: '+str(filepath)+'\ngallerypath: '+ \
                        str(self.gallerypath)+'\ncommonprefix: '+str(commonprefix))
            return False
        
        elif len(self.getFileByHash(md5hash))>0:
            logger.error('File with same hash is already in database')
            return False
        
        else:
            title = os.path.splitext(os.path.basename(filepath))[0]
            filepath_rel = os.path.relpath(filepath, commonprefix)
            logger.debug('File relative path -> '+str(filepath_rel))
            
            self.dbmodel.addFile(filehash=md5hash, filepath=filepath_rel, title=title)
            return True
        
    def getFileByHash(self, filehash):
        """
        Returns fileinfo
        """
        info = self.dbmodel.getFilesByHash(filehash)
        return info
    
    # TODO - finish this
    def search(self, searchstring):
        """
        Returns filtered list of files
        """
        searchstring = searchstring.lower()
        all_files = self.dbmodel.getFiles()

        filtered = []
        for f in all_files:
            eq = False
            if searchstring == '':
                eq = True
            elif searchstring == f['title']:
                eq = True
            elif searchstring == f['title_jpn']:
                eq = True
            elif searchstring == f['category']:
                eq = True
            elif searchstring in f['tags']:
                eq = True
            
            if eq == True:
                filtered.append(f)
                        
        return filtered
        
    def updateFileInfo(self, filehash, newinfo):
        self.dbmodel.updateFile(filehash, newinfo)
    
    def infoFromEHentaiLink(self, ehlink):
        """
        Returns ehentai.org gallery metdata from gallery link.
        """
        index = ehlink.find('hentai.org/g/')
        splited = ehlink[(index+13):].split('/')
        
        gallery_id = splited[0]
        gallery_token = splited[1]
        
        logger.debug('EH id - '+str(gallery_id)+' token - '+str(gallery_token))
        
        return self.infoFromEHentai(gallery_id, gallery_token)
    
    def infoFromEHentai(self, gallery_id, gallery_token):
        """
        Returns ehentai.org gallery metadata from gallery_id and gallery_token.
        http://ehwiki.org/wiki/API
        """
        payload = json.dumps({'method': 'gdata', 'gidlist': [[gallery_id, gallery_token]]})
        headers = {'content-type': 'application/json'}
        
        r = requests.post("http://g.e-hentai.org/api.php", data=payload, headers=headers)
        gallery_info = r.json()['gmetadata'][0]
        
        return gallery_info 
        
    def updateFileInfoEHentai(self, filehash, ehlink):
        originfo = self.getFileByHash(filehash)[0]
        ehinfo = self.infoFromEHentaiLink(ehlink)
        ehinfo['filepath'] = originfo['filepath']
        
        self.updateFileInfo(filehash, ehinfo)
        
        
