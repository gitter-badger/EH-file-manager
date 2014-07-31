# ! /usr/bin/python
# coding: utf-8
"""
This file is part of EH File Manager.

EH File Manager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
any later version.

EH File Manager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with EH File Manager.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
logger = logging.getLogger(__name__)

import os
import hashlib
import re
from operator import itemgetter
import shutil
import time
import yaml
import tempfile
from PIL import Image

from database_model import DatabaseModel
from settings import Settings
from eh_fetcher import EHFetcher
from fakku_fetcher import FakkuFetcher
import decompressor

class GalleryManager():
    """
    Main class of application
    """
    CONFIGDIR = '.config'
    THUMBDIR = 'thumb'
    COOKIEFILE = 'cookies.yaml'
    THUMB_MAXSIZE = 180, 270
    
    def __init__(self, gallerypath=''):
        self.gallerypath = str(gallerypath)
        
        self.configpath = None
        self.thumbpath = None
        
        self.dbmodel = None
        self.settings = None
        self.ehfetcher = None
        self.fakkufetcher = None
        
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
        
        # def paths
        self.configpath = os.path.join(self.gallerypath, self.CONFIGDIR)
        self.thumbpath = os.path.join(self.configpath, self.THUMBDIR)
        
        # load settings
        self.settings = Settings(self.configpath)
        self.settings.loadSettings()
            
        # open connection to database
        self.dbmodel = DatabaseModel(self.configpath)
        self.dbmodel.openDatabase()   
        
        # init fetchers
        self.ehfetcher = EHFetcher(self)
        self.fakkufetcher = FakkuFetcher()
    
    def isGallery(self, path):
        """
        Checks if path leads to existing gallery.
        """
        configpath = os.path.join(str(path), self.CONFIGDIR)
        thumbpath = os.path.join(configpath, self.THUMBDIR)
        
        if os.path.isdir(configpath):
            database_path = os.path.join(configpath, DatabaseModel.FILENAME)
            
            if os.path.isfile(database_path) and os.path.isdir(thumbpath):
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
        thumbpath = os.path.join(configpath, self.THUMBDIR)
        
        # create config folder and files
        if not os.path.isdir(configpath):
            os.mkdir(configpath)
        if not os.path.isdir(thumbpath):
            os.mkdir(thumbpath)
        DatabaseModel(configpath)
        setmod = Settings(configpath)
        setmod.loadSettings()
        setmod.saveSettings()
        
    def getSettings(self):
        return self.settings.getSettings()
        
    def getDefaultSettings(self):
        return self.settings.getDefaultSettings()
        
    def saveSettings(self, newSettings):
        self.settings.setSettings(newSettings)
        self.settings.saveSettings()
    
    def getHash(self, filepath):
        """
        Returns hash of file.
        """
        
        afile = open(filepath, 'rb')
        buf = afile.read()
        afile.close()
        
        hasher = hashlib.sha1()
        hasher.update(buf)
        
        filehash = hasher.hexdigest()
        logger.debug('Generated sha1 hash - '+str(filehash))
        
        return filehash
        
    def addFile(self, filepath, filehash = None):
        """
        Add fileinfo to database
        """
        logger.debug('Processing file - '+filepath)
        if filehash is None:
            filehash = self.getHash(filepath)
        
        # get relative filepath to gallery path
        commonprefix = os.path.commonprefix([self.gallerypath, filepath])
        if commonprefix != self.gallerypath:
            logger.error('File is not in child directory of gallery!!!'+ \
                        '\nfilepath: '+filepath+'\ngallerypath: '+ \
                        str(self.gallerypath)+'\ncommonprefix: '+commonprefix)
            return False
        
        elif len(self.getFileByHash(filehash))>0:
            logger.error('File with same hash is already in database')
            return False
        
        else:
            title = os.path.splitext(os.path.basename(filepath))[0]
            filepath_rel = os.path.relpath(filepath, commonprefix)
            logger.debug('File relative path -> '+filepath_rel)
            
            # add file to database
            self.dbmodel.addFile(filehash=filehash, filepath=filepath_rel, title=title)
            
            # get thumbnail
            try:
                self.getThumb(filepath, filehash)
            except Exception, e:
                logger.error('Other error when generating thumb: '+str(e))
            
            return True
              
    def removeFile(self, filehash):
        self.dbmodel.removeFile(filehash)
        
        thumb_path = os.path.join(self.thumbpath, filehash+'.png')
        if os.path.isfile(thumb_path):
            os.remove(thumb_path)
        
    def getFileByHash(self, filehash):
        """
        Returns fileinfo
        """
        info = self.dbmodel.getFilesByHash(filehash)
        return info
    
    def getFileList(self, path=None):
        """
        Returns list of lists:
            [str filepath, str hash, bool inDatabase]
        """
        if path is None:
            path = self.gallerypath
        
        logger.debug('Getting list of files in database...')
        filepathlist = []
        for root, dirs, files in os.walk(unicode(path)):
            if os.path.commonprefix([self.configpath, root]) != self.configpath:
                paths = [os.path.join(root,f) for f in files]
                filepathlist+=paths
        
        # Filter by extension
        if len(self.getSettings()['allowed_extensions']) > 0:
            filepathlist_new = []
            for filepath in filepathlist:
                ext = os.path.basename(filepath).split('.')[-1]
                if ext in self.getSettings()['allowed_extensions']:
                    filepathlist_new.append(filepath)
                    
            filepathlist = filepathlist_new
        
        logger.debug('Found '+str(len(filepathlist))+' files. Getting hash + database state...')
        filelist = []
        for filepath in filepathlist:
            filehash = self.getHash(filepath)
            indb = len(self.getFileByHash(filehash))>0
            
            filelist.append([filepath, filehash, indb])
                
        return filelist
        
    def addFiles(self, filelist, new=False):
        """
        if new==True adds only files that are not in database
        [str filepath, str filehash, bool inDatabase]
        returns number of files added
        """
        logger.debug('Adding files to database...')
        
        added = 0
        for f in filelist:
            if new and not f[2]:
                self.addFile(filepath = f[0], filehash = f[1])
                added+=1
                
        logger.debug('Added '+str(len(filelist))+' files to database.')
        
        return added
            
    # TODO - finish this (- * % _) http://ehwiki.org/wiki/search
    def search(self, searchstring, search_cfg = {}):
        """
        Returns filtered list of files
        Example of searchstring:
            male:glasses "fate zero" artist:"kosuke haruhito" blowjob
        Search cfg:
            {
            'new': bool,
            'del': bool,
            'categories': list(str),
            'categories_other': bool,
            'sort': str,
            'sort_rev': bool
            }
        """
        # overwrite default search settings
        default_search_cfg = {
                            'new': False,
                            'del': False,
                            'categories': [],
                            'categories_other': True,
                            'sort': 'published',
                            'sort_rev': False
                            }
        default_search_cfg.update(search_cfg)
        search_cfg = default_search_cfg
        
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
                    eq = False
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
                            for t in f['tags'][tag_c]:
                                if s in t:
                                    eq = True
                        
                        if eq == False:
                            break
                    else:
                        #has tag category              
                        if s[0] in f['tags']:
                            for t in f['tags'][s[0]]:
                                if s[1] in t:
                                    eq = True
                                    
                        elif s[0] == 'hash':
                            if s[1] == f['hash'].lower():
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
        
        # category filters
        filtered_new = []
        for f in filtered:
            # append OTHER categories
            if not (f['category'].lower().strip() in self.getSettings()['categories']) \
            and not (f['category'].lower().strip() in search_cfg['categories']) \
            and search_cfg['categories_other']:
                filtered_new.append(f)
                continue
            
            # append standard categories
            for c in search_cfg['categories']:
                if f['category'].lower().strip() == c.lower().strip():
                    filtered_new.append(f)
            
        filtered = filtered_new 
            
        # Sort results
        if search_cfg['sort'] == 'published':
            search_cfg['sort_rev'] = not search_cfg['sort_rev']
        filtered = sorted(filtered, key=itemgetter(search_cfg['sort']), reverse=search_cfg['sort_rev']) 
             
        return filtered
        
    def updateFileInfo(self, filehash, newinfo):
        self.dbmodel.updateFile(filehash, newinfo)
        
    def fixFilepaths(self):
        """
        requirements: 1 file == 1 unique hash
        """
        all_files = self.dbmodel.getFiles()
        missing_files = []
        for f in all_files:
            if not os.path.isfile(os.path.join(self.gallerypath, f['filepath'])):
                missing_files.append(f)
        
        logger.info('Found '+str(len(missing_files))+' wrong filepaths in database')
        
        if len(missing_files)!=0:
            gallery_filelist = self.getFileList()
        
        for mf in missing_files:
            for fl in gallery_filelist:
                if fl[1] == mf['hash']:
                    logger.debug('Found file in new location: '+fl[0])
                    mf['filepath'] = fl[0]
                    self.updateFileInfo(mf['hash'], mf)
                    break
        
    def loginToEH(self, username, password):
        """
        Returns if login was sucessfull
        """
        cookies = self.ehfetcher.loginToEH(username, password)
        if self.ehfetcher.getLoggedIn(cookies):
            self.ehfetcher.setCookies(cookies)
            return True
        else:
            self.ehfetcher.setCookies({})
            return False
            
    def getLogin(self):
        """
        Returns True if logged in
        """
        return self.ehfetcher.getLoggedIn()
            
    def saveCookies(self, cookies=None):
        """
        Saves cookies to file for future reuse (autologin)
        """
        logger.debug('Saving cookies to file...')
        if cookies is None:
            cookies = self.ehfetcher.getCookies()
        try:
            f = open(os.path.join(self.configpath, self.COOKIEFILE), 'wb')
            yaml.dump(cookies, f)
            f.close
        except Exception, e:
            logger.error('Saving cookies to file failed!! '+str(e))
        else:
            logger.debug('Cookies saved')
    
    def loadSavedCookies(self):
        """
        Reads cookies from file and if they are correct loads them to eh_fetcher
        Returns:
            True - cookies loaded from file and login was sucessfull
            False - error
        """
        logger.debug('Loading cookies from file...')
        try:
            f = open(os.path.join(self.configpath, self.COOKIEFILE), 'rb')
            cookies = yaml.load(f)
            f.close()
        except Exception, e:
            logger.error('Loading cookies from file failed!! '+str(e))
            return False

        if self.ehfetcher.getLoggedIn(cookies):
            self.ehfetcher.setCookies(cookies)
        else:
            logger.error('Bad saved cookies!!')
            return False
        
        logger.debug('Cookies loaded')
        return True
    
    def getThumb(self, filepath, filehash):
        """
        Creates thumbnail from first page in archive.
        Thumbnail is saved as FILEHASH.png in THUMBDIR.
        
        Returns:
            False - if ERROR
            True - if OK
        """
        logger.debug('Creating thumbnail...')
        
        # open archive
        try:
            archive = decompressor.ArchiveFile(filepath)
        except Exception, e:
            logger.warning('Error openning File: %s', filepath)
            logger.debug(str(e))
            return False
        
        # get list of files in archive
        filelist = archive.namelist()
        
        # filter out files that are not images
        filtered_filelist = []
        for f in filelist:
            if f.lower().split('.')[-1] in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
                filtered_filelist.append(f)

        # get path to first page
        filtered_filelist.sort()
        try:
            file_to_use = filtered_filelist[0]
        except Exception, e:
            logger.error('No images in archive file - thumb generation failed: '+str(e))
            return False
        
        # extract first page
        try:
            f = tempfile.NamedTemporaryFile()
            f.write(archive.open(file_to_use))
        except Exception, e:
            logger.warning('Error uncompressing File: %s', filepath)
            logger.debug(str(e))
            archive.close()
            return False

        # create thumbnail
        im = Image.open(f.name)
        f.close()
        im.thumbnail(self.THUMB_MAXSIZE, Image.ANTIALIAS)
        new_filename = filehash+'.png'
        final_path = os.path.join(self.thumbpath, new_filename)
        try:
            im.save(final_path, "PNG")
        except Exception, e:
            logger.warning('Couldnt save thumb for: %s', filepath)
            logger.debug(str(e))
            return False

        return True
    
    def updateFileInfoLink(self, filehash, link):
        """
        Returns:
            EH fetcher error code (if %10==0: OK)
        """
        # add schema to link
        if not (link.startswith('http://') or link.startswith('https://')):
            link = 'http://'+link
        
        if 'fakku.net' in link:
            #try:
            info = self.fakkufetcher.infoFromFakkuLink(link)
            #except Exception, e:
                #logger.error('Error when getting info from fakku: '+str(e))
                #return 101
            err = 0
        elif 'hentai.org' in link:
            info, err = self.ehfetcher.infoFromEHentaiLink(link)
        else:
            logger.error('Not supported website')
            return 101
            
        if err%10!=0:
            logger.warning('URL update failed')
            return err
        
        originfo = self.getFileByHash(filehash)[0]
        originfo.update(info)
        
        originfo['new'] = False
            
        self.updateFileInfo(filehash, originfo)
        
        return err
        
    def findFileOnEH(self, filehash):
        """
        Returns:
            result - list of galleries
            err - EH fetcher error code
            31 - sha1hash of image couldnt be generated
        """
        filepath_rel = self.getFileByHash(filehash)[0]['filepath']
        filepath = os.path.join(self.gallerypath, filepath_rel)
        
        result = []
        sha1hash = self.ehfetcher.getHashOfFileInGallery(filepath)
        if sha1hash is not None:
            logger.debug('Searching by filehash...')
            result, err = self.ehfetcher.searchEHByFileHash(sha1hash)
        else:
            err = 31
        
        return result, err
        
