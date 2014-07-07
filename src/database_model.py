# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sqlite3

class DatabaseModel():
    def __init__(self, configpath):
        self.configpath = configpath
        self.dbfilename='database.db'
        
        self.dbpath = None
        self.liteconnection = None
        self.litecursor = None
        
    def openDatabase(self):
        """
        Creates connection with database. if database doesnt exists creates new one.
        """
        self.dbpath = os.path.join(self.configpath, self.dbfilename)
        
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
        
    def tagsToString(self, tags):
        """
        converts list of tags to string that can be inserted into database.
        """
        tagstr = ''
        for tc in tags:
            tagstr+=' '+' '.join([str(tc).lower()+':'+t.replace(' ','_').lower() for t in tags[tc]])
            
        return tagstr.strip()
        
    def stringToTags(self, tagstr):
        """
        Converts string gotten from database to list of tags.
        """
        tags = {}
        if tagstr!='':
            taglist = tagstr.split(' ')
            for t in taglist:
                splited = t.split(':')
                if len(splited) == 1:
                    cat = 'misc'
                    tag = unicode(splited[0].replace('_',' ').lower()).encode("utf8")
                else:
                    cat = unicode(splited[0].lower()).encode("utf8")
                    tag = unicode(splited[1].replace('_',' ').lower()).encode("utf8")
                
                if cat in tags:
                    tags[cat].append(tag)
                else:
                    tags[cat] = [tag]
            
        return tags
        
    def addFile(self, filehash, filepath, title, title_jpn='', category='Manga', tags=[]):
        fileinfo = {
                    'hash': str(filehash),
                    'filepath': str(filepath),
                    'title': str(title),
                    'title_jpn': str(title_jpn),
                    'category': str(category),
                    'tags': {}
                    } 
        self.addFileInfo(fileinfo)
    
    def addFileInfo(self, fileinfo):
        """
        fileinfo = {
                    'hash': '',
                    'filepath': '',
                    'title': '',
                    'title_jpn': '',
                    'category': '',
                    'tags': {}
                    }    
        """ 
        # convert tags to string
        fileinfo['tags'] = self.tagsToString(fileinfo['tags'])
                
        query = unicode("INSERT INTO Files VALUES ('"+fileinfo['hash']+"', '"+fileinfo['filepath']+"', '"+fileinfo['title']+"', '"+fileinfo['title_jpn']+"', '"+fileinfo['category']+"', '"+fileinfo['tags']+"' )").encode("utf8")
        logger.debug('SQLite newfile query: '+query)
        
        self.litecursor.execute(query)
        self.liteconnection.commit()
    
    def resultToDictionary(self, result):
        """
        returns fetched sqlresult as list of dictionaries
        """
        fileinfo = []
        for i in range(0,len(result)):
            fileinfo.append({
                        'hash': result[i][0],
                        'filepath': result[i][1],
                        'title': result[i][2],
                        'title_jpn': result[i][3],
                        'category': result[i][4],
                        'tags': result[i][5]
                        })
        
        for r in fileinfo:
            r['tags'] = self.stringToTags(r['tags'])
                
        return fileinfo
    
    def getFiles(self):
        self.litecursor.execute("SELECT * FROM Files")
        returned_data = self.litecursor.fetchall()
        return self.resultToDictionary(returned_data)
    
    def getFilesByHash(self, filehash):
        self.litecursor.execute("SELECT * FROM Files WHERE hash = '"+filehash+"' ")
        returned_data = self.litecursor.fetchall()
        return self.resultToDictionary(returned_data)
        
    def updateFile(self, filehash, newinfo):
        # convert tags to string
        newinfo['tags'] = self.tagsToString(newinfo['tags'])
        
        query = unicode("UPDATE Files SET filepath='"+newinfo['filepath']+"', title='"+newinfo['title']+"', title_jpn='"+newinfo['title_jpn']+"', category='"+newinfo['category']+"', tags='"+newinfo['tags']+"' WHERE hash = '"+filehash+"' ").encode("utf8")
        logger.debug('SQLite updatefile query: '+query)
        
        self.litecursor.execute(query)
        self.liteconnection.commit()
        
    def removeFile(self, filehash):
        query = "DELETE FROM Files WHERE hash='"+filehash+"'"
        logger.debug('SQLite delete query: '+query)
        
        self.litecursor.execute(query)
        self.liteconnection.commit()
