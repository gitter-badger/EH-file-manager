# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

import argparse
import os
import sqlite3

class ManMan():
    """
    Main class of application
    """
    
    def __init__(self, gallerypath=None):
        self.gallerypath = gallerypath
        self.liteconnection = None
        self.litecursor = None
        
        if self.gallerypath is not None:
            self.open_path(self.gallerypath)
    
    def open_path(self, path):
        self.gallerypath = path
        # checks if path is existing gallery. if not creates one.
        if self.is_gallery(self.gallerypath) is False:
            self.init_gallery(self.gallerypath)
            
        # open connection to database
        self.liteconnection = sqlite3.connect(os.path.join(path,".manman/database.db"))
        self.litecursor = self.liteconnection.cursor()
        
        # print sqldatabase info
        logger.debug("SQLite version: %s", sqlite3.sqlite_version)    
    
    def is_gallery(self, path):
        if os.path.isdir(os.path.join(path,".manman")) is True:
            logger.debug('Path is gallery.')
            return True
        else:
            logger.debug('Path is not gallery.')
            return False
        
    def init_gallery(self, path, destructive=False):
        logger.debug('Creating new gallery structure...')
        
        # create folder structure
        os.mkdir(os.path.join(path,".manman"))
        os.mkdir(os.path.join(path,"Files"))
        
        # init database
        liteconnection = sqlite3.connect(os.path.join(path,".manman/database.db"))
        litecursor = liteconnection.cursor()
        litecursor.execute('''CREATE TABLE files (name text, route text, hash text, tags text)''')
        liteconnection.commit()
        liteconnection.close()
    
def main():
    # Parasing input prarmeters
    parser = argparse.ArgumentParser(
        description='ManMan (Manga Manager)'
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
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
        
    if args.nogui:
        logger.debug('Running without gui.')
        gallery = ManMan()
        gallery.open_path(args.gallery)
    else:
        logger.debug('Running with gui.')
    
    
if __name__ == "__main__":
    main()
