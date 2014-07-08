# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys
import hashlib
import re

import requests
import json
from bs4 import BeautifulSoup

from database_model import DatabaseModel
from settings import Settings

class GalleryManager():
    """
    Main class of application
    """
    CONFIGDIR = '.config'
    
    def __init__(self, gallerypath=''):
        self.gallerypath = str(gallerypath)
        
        self.dbmodel = None
        self.settings = None
        
        if self.gallerypath is not '':
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
        self.gallerypath = os.path.abspath(str(path))
        # checks if path is existing gallery. if not creates one.
        if self.isGallery(self.gallerypath) is False:
            self.initGallery(self.gallerypath)
        
        
        configpath = os.path.join(self.gallerypath, self.CONFIGDIR)
        # load settings
        self.settings = Settings(configpath)
        self.settings.loadSettings()
            
        # open connection to database
        self.dbmodel = DatabaseModel(configpath)
        self.dbmodel.openDatabase()   
    
    def isGallery(self, path):
        """
        Checks if path leads to existing gallery.
        """
        configpath = os.path.join(str(path), self.CONFIGDIR)
        
        if os.path.isdir(configpath):
            settings_path = os.path.join(configpath, Settings.FILENAME)
            database_path = os.path.join(configpath, DatabaseModel.FILENAME)
            
            if os.path.isfile(settings_path) and os.path.isfile(database_path):
                logger.debug('isGallery: given path is existing gallery.')
                return True
            
        logger.debug('isGallery: given path is not gallery.')
        return False
        
    def initGallery(self, path):
        """
        Creates new gallery basic structure.
        """
        logger.debug('Creating new gallery structure...')
        
        configpath = os.path.join(path, self.CONFIGDIR)
        
        # create config folder and files
        if not os.path.isdir(configpath):
            os.mkdir(configpath)
        DatabaseModel(configpath)
        setmod = Settings(configpath)
        setmod.loadSettings()
        setmod.saveSettings()
        
    def getSettings(self):
        return self.settings.getSettings()
        
    def saveSettings(self, newSettings):
        self.settings.setSettings(newSettings)
        self.settings.saveSettings()
    
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
        
    def addFile(self, filepath, filehash = None):
        """
        Add fileinfo to database
        """
        logger.debug('Processing file - '+str(filepath))
        if filehash is None:
            filehash = self.getHash(filepath)
        
        # get relative filepath to gallery path
        commonprefix = os.path.commonprefix([self.gallerypath, filepath])
        if commonprefix != self.gallerypath:
            logger.error('File is not in child directory of gallery!!!'+ \
                        '\nfilepath: '+str(filepath)+'\ngallerypath: '+ \
                        str(self.gallerypath)+'\ncommonprefix: '+str(commonprefix))
            return False
        
        elif len(self.getFileByHash(filehash))>0:
            logger.error('File with same hash is already in database')
            return False
        
        else:
            title = os.path.splitext(os.path.basename(filepath))[0]
            filepath_rel = os.path.relpath(filepath, commonprefix)
            logger.debug('File relative path -> '+str(filepath_rel))
            
            self.dbmodel.addFile(filehash=filehash, filepath=filepath_rel, title=title)
            return True
        
    def getFileByHash(self, filehash):
        """
        Returns fileinfo
        """
        info = self.dbmodel.getFilesByHash(filehash)
        return info
    
    def getFileList(self, path=None, excludeDotfiles=True):
        """
        Returns list of lists:
            [str filepath, str hash, bool inDatabase]
        """
        if path is None:
            path = self.gallerypath
        
        logger.debug('Getting list of files in database...')
        filepathlist = []
        for root, dirs, files in os.walk(path):
            if not os.path.basename(root).startswith('.') and excludeDotfiles:
                paths = [os.path.join(root,f) for f in files]
                filepathlist+=paths
        
        logger.debug('Found '+str(len(filepathlist))+' files. Getting hash + database state...')
        filelist = []
        for filepath in filepathlist:
            filehash = self.getHash(filepath)
            indb = len(self.getFileByHash(filehash))>0
            
            filelist.append([filepath, filehash, indb])
                
        return filelist
        
    def addNewFiles(self):
        """
        Adds new files in gallery to database
        returns number of newfiles added
        """
        filelist = self.getFileList()
        
        logger.debug('Adding new files to database...')
        newfiles = 0
        for f in filelist:
            if f[2] is False:
                self.addFile(filepath = f[0], filehash = f[1])
                newfiles+=1
        
        logger.debug('Added '+str(newfiles)+' new files to database.')
        return newfiles
            
    # TODO - finish this (- * % _) http://ehwiki.org/wiki/search
    def search(self, searchstring, search_cfg):
        """
        Returns filtered list of files
        Example of searchstring:
            male:glasses "fate zero" artist:"kosuke haruhito" blowjob
        """
        all_files = self.dbmodel.getFiles()
        searchstring = unicode(searchstring.lower()).encode("utf8")
        
        
        if searchstring=='':
            filtered = all_files
        else:
            # split string (but ignore spaces inside "")
            PATTERN = re.compile(r'''((?:[^\s"']|"[^"]*"|'[^']*')+)''')
            search_strs = PATTERN.split(searchstring)[1::2]

            filtered = []
            for f in all_files:
                eq = False
                for s in search_strs:
                    # remove quotes and split (category:tag)
                    s = s.replace('"', '').replace("'",'')
                    s = s.split(':')
                    
                    if len(s) == 1:
                        #no tag category
                        s = s[0]
                        
                        if s in f['hash'].lower():
                            eq = True
                        
                        if (s in f['title'].lower()) or (s in f['title_jpn'].lower()):
                            eq = True
                            
                        for tag_c in f['tags']:
                            if s in f['tags'][tag_c]:
                                eq = True
                        
                        if eq == False:
                            break
                    else:
                        #has tag category              
                        if s[0] in f['tags']:
                            if s[1] in f['tags'][s[0]]:
                                eq = True
                        elif s[0] == 'hash':
                            if s[1] in f['hash'].lower():
                                eq = True
                        
                        if eq == False:
                            break
                            
                if eq == True:
                    filtered.append(f)
                    
        # filter by search settings
        if search_cfg['new']:
            filtered_new = []
            for f in filtered:
                if f['new']:
                    filtered_new.append(f)
            filtered = filtered_new
        
        if search_cfg['del']:
            filtered_new = []
            for f in filtered:
                if not os.path.isfile(os.path.join(self.gallerypath, f['filepath'])):
                    filtered_new.append(f)
            filtered = filtered_new 
             
        return filtered
        
    def updateFileInfo(self, filehash, newinfo):
        self.dbmodel.updateFile(filehash, newinfo)
    
    def infoFromEHentaiLink(self, ehlink, api=False):
        """
        Returns ehentai.org gallery metdata from gallery link.
        """
        if api:
            index = ehlink.find('hentai.org/g/')
            splited = ehlink[(index+13):].split('/')
            
            gallery_id = splited[0]
            gallery_token = splited[1]
            
            logger.debug('EH id - '+str(gallery_id)+' token - '+str(gallery_token))
            
            return self.infoFromEHentai_API(gallery_id, gallery_token)
        else:
            return self.infoFromEHentai_HTML(ehlink)
        
    def infoFromEHentai_API(self, gallery_id, gallery_token):
        """
        Returns ehentai.org gallery metadata from gallery_id and gallery_token.
        http://ehwiki.org/wiki/API
        """
        payload = json.dumps({'method': 'gdata', 'gidlist': [[gallery_id, gallery_token]]})
        headers = {'content-type': 'application/json'}
        
        r = requests.post("http://g.e-hentai.org/api.php", data=payload, headers=headers)
        gallery_info = r.json()['gmetadata'][0]
        
        gallery_info['tags'] = {'misc':gallery_info['tags']}
        gallery_info['category'] = gallery_info['category'].lower()
        
        return gallery_info 
        
    def infoFromEHentai_HTML(self, ehlink):
        """
        Returns ehentai.org gallery metadata parsed from html file.
        """
        fileinfo = {}
        
        r = requests.get(ehlink)
        html = unicode(r.text).encode("utf8")
        soup = BeautifulSoup(html)

        div_gd2 = soup.body.find('div', attrs={'id':'gd2'})
        fileinfo['title'] = div_gd2.find('h1', attrs={'id':'gn'}).text
        fileinfo['title_jpn'] = div_gd2.find('h1', attrs={'id':'gj'}).text

        div_gd3 = soup.body.find('div', attrs={'id':'gd3'})
        fileinfo['category'] = div_gd3.find('img').get('alt')

        left_text = div_gd3.find('div', attrs={'id':'gdd'}).text
        fileinfo['language'] = left_text[left_text.find('Language:')+9:]

        div_gd4 = soup.body.find('div', attrs={'id':'gd4'})
        div_taglist = div_gd4.find('div', attrs={'id':'taglist'}).find_all('tr')
        fileinfo['tags'] = {}
        for tl in div_taglist:
            tds = tl.find_all('td')
            cat = tds[0].text[:tds[0].text.find(':')]
            tags = [t.text for t in tds[1].find_all('a')] 
            
            fileinfo['tags'][cat] = tags

        return fileinfo
        
    def updateFileInfoEHentai(self, filehash, ehlink, api=False):
        # add schema to link
        if not (ehlink.startswith('http://') or ehlink.startswith('https://')):
            ehlink = 'http://'+ehlink
        
        originfo = self.getFileByHash(filehash)[0]
        ehinfo = self.infoFromEHentaiLink(ehlink, api)
        ehinfo['filepath'] = originfo['filepath']
        ehinfo['new'] = False
        
        self.updateFileInfo(filehash, ehinfo)
        
    def removeFile(self, filehash):
        self.dbmodel.removeFile(filehash)
        
        
