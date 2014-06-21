# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

import argparse
import os
import hashlib

from database_model import DatabaseModel

class Man2():
    """
    Main class of application
    """
    
    def __init__(self, gallerypath=None, configdir='.config'):
        self.gallerypath = gallerypath
        self.configdir = configdir
        self.dbmodel = None
        
        if self.gallerypath is not None:
            self.open_path(self.gallerypath)
    
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
    
def main():
    # Parasing input prarmeters
    parser = argparse.ArgumentParser(
        description='Man2 (Manga Manager)'
    )
    parser.add_argument(
        '-g', '--gallery',
        default=None,
        help='Path to directory with manga gellery')
    parser.add_argument(
        '--nogui',
        action='store_true',
        help='Disable GUI')
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Debug mode')
    args = parser.parse_args()
    
    # Logger configuration
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
        
    if args.nogui:
        logger.debug('Running without gui.')
        gallery = Man2()
        gallery.open_path(args.gallery)
        testfilepath = os.path.join(args.gallery, 'Files/test.zip')
        #gallery.process_file(testfilepath)
        print gallery.get_file_info(testfilepath)
    else:
        logger.debug('Running with gui.')
    
    
if __name__ == "__main__":
    main()
