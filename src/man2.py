# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

import argparse
import os

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
    else:
        logger.debug('Running with gui.')
    
    
if __name__ == "__main__":
    main()
