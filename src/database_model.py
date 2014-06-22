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
        
    def openDatabase(self, dbfilename='database.db'):
        """
        Creates connection with database. if database doesnt exists creates new one.
        """
        self.dbpath = os.path.join(os.path.join(self.gallerypath, self.configdir), dbfilename)
        
        # if database doesnt exist create it
        if os.path.isfile(self.dbpath) is False:
            self.initDatabase()
        
        # create connection to databse
        self.liteconnection = sqlite3.connect(self.dbpath)
        self.litecursor = self.liteconnection.cursor()
        
        # print sqldatabase info
        logger.debug("SQLite version: %s", sqlite3.sqlite_version)  
        
    def closeDatabase(self):
        self.liteconnection.commit()
        self.liteconnection.close()
        logger.debug('Connection with database was closed.')
        
    def initDatabase(self):
        """
        Creates new database file.
        """
        liteconnection = sqlite3.connect(self.dbpath)
        litecursor = liteconnection.cursor()
        litecursor.execute("CREATE TABLE Files (hash text, filepath text, title text, title_jpn text, category text, tags text)")
        liteconnection.commit()
        liteconnection.close()
        
    def addFile(self, filehash, filename, names={'eng':'','jp':''}, category='Manga', tags=[]):
        tags_processed = ' '.join(tags)
                
        query = "INSERT INTO Files VALUES ('"+filehash+"', '"+filename+"', '"+str(names['eng'])+"', '"+str(names['jp'])+"', '"+str(category)+"', '"+tags_processed+"' )"
        logger.debug('SQLite newfile query: '+str(query))
        
        self.litecursor.execute(query)
        self.liteconnection.commit()
    
    def getFiles(self):
        self.litecursor.execute("SELECT * FROM Files")
        returned_data = self.litecursor.fetchall()
        
        return returned_data
    
    def getFilesByHash(self, filehash):
        self.litecursor.execute("SELECT * FROM Files WHERE hash = '"+filehash+"' ")
        returned_data = self.litecursor.fetchall()
        
        return returned_data
        
    
        
