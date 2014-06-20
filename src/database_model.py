# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sqlite3

class DatabaseModel():
    def __init__(self, gallerypath, configdir='.config'):
        # path to database file
        self.gallerypath = gallerypath
        self.configdir = configdir
        self.dbpath = None
        self.liteconnection = None
        self.litecursor = None
        
    def open_database(self, dbfilename='database.db'):
        """
        Creates connection with database. if database doesnt exists creates new one.
        """
        self.dbpath = os.path.join(os.path.join(self.gallerypath, self.configdir), dbfilename)
        
        # if database doesnt exist create it
        if os.path.isfile(self.dbpath) is False:
            self.init_database()
        
        # create connection to databse
        self.liteconnection = sqlite3.connect(self.dbpath)
        self.litecursor = self.liteconnection.cursor()
        
        # print sqldatabase info
        logger.debug("SQLite version: %s", sqlite3.sqlite_version)   
        
    def init_database(self):
        """
        Creates new database file.
        """
        liteconnection = sqlite3.connect(self.dbpath)
        litecursor = liteconnection.cursor()
        litecursor.execute('''CREATE TABLE files (name text, route text, hash text, tags text)''')
        liteconnection.commit()
        liteconnection.close()
