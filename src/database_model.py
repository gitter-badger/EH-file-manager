# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sqlite3
import time

class DatabaseModel():
    FILENAME = 'database.db'
    
    def __init__(self, configpath):
        self.configpath = configpath
        
        self.dbpath = None
        self.liteconnection = None
        self.litecursor = None
        
    def openDatabase(self):
        """
        Creates connection with database. if database doesnt exists creates new one.
        """
        self.dbpath = os.path.join(self.configpath, self.FILENAME)
        
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
        litecursor.execute("CREATE TABLE Files (hash text, published int, filepath text, title text, title_jpn text, category text, tags text, new bool)")
        liteconnection.commit()
        liteconnection.close()
        
    def tagsToString(self, tags):
        """
        converts list of tags to string that can be inserted into database.
        """
        tagstr = ''
        for tc in tags:
            tagstr+=' '+' '.join([str(tc).lower()+':'+t.replace(' ','_').lower() for t in tags[tc]])
        
        # remove forbidden chars in string
        tagstr = tagstr.replace("'",'').replace('"','')
        
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
        
    def addFile(self, filehash, filepath, title, title_jpn='', category='manga', tags=[]):
        fileinfo = {
                    'hash': filehash,
                    'published': int(time.time()),
                    'filepath': filepath,
                    'title': title,
                    'title_jpn': title_jpn,
                    'category': category,
                    'tags': {},
                    'new': 1
                    } 
        self.addFileInfo(fileinfo)
    
    def addFileInfo(self, fileinfo):
        """
        fileinfo = {
                    'hash': '',
                    'published': bool,
                    'filepath': '',
                    'title': '',
                    'title_jpn': '',
                    'category': '',
                    'tags': {},
                    'new': bool
                    }    
        """ 
        # convert tags to string
        fileinfo['tags'] = self.tagsToString(fileinfo['tags'])
        
        # convert new to string
        fileinfo['new'] = str(int(fileinfo['new']))
        
        # convert utf-8 to unicode
        for fi in fileinfo:
            if type(fileinfo[fi]) != type(u' ') and isinstance(fileinfo[fi], basestring):
                fileinfo[fi] = fileinfo[fi].decode('utf-8') 
                
        logger.debug('SQLite newfile query: '+str(fileinfo))
        
        values = (fileinfo['hash'], fileinfo['published'], fileinfo['filepath'], 
                  fileinfo['title'], fileinfo['title_jpn'], fileinfo['category'], 
                  fileinfo['tags'], fileinfo['new'])
        self.litecursor.execute(u'INSERT INTO Files VALUES (?, ?, ?, ?, ?, ?, ?, ?)', values)
        self.liteconnection.commit()
    
    def resultToDictionary(self, result):
        """
        returns fetched sqlresult as list of dictionaries
        """
        fileinfo = []
        for i in range(0,len(result)):
            fileinfo.append({
                        'hash': result[i][0],
                        'published': result[i][1],
                        'filepath': result[i][2],
                        'title': result[i][3],
                        'title_jpn': result[i][4],
                        'category': result[i][5],
                        'tags': result[i][6],
                        'new': bool(int(result[i][7]))
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
        
        # convert new to string
        newinfo['new'] = str(int(newinfo['new']))
        
        # convert utf-8 to unicode
        for ni in newinfo:
            if type(newinfo[ni]) != type(u' '):
                if type(newinfo[ni]) == type(' '):
                    newinfo[ni] = newinfo[ni].decode('utf-8') 
                else:
                    newinfo[ni] = unicode(newinfo[ni])
                
        logger.debug('SQLite updatefile query: '+str(newinfo))
        
        values = (newinfo['filepath'], newinfo['published'], newinfo['title'],
                  newinfo['title_jpn'], newinfo['category'], newinfo['tags'],
                  newinfo['new'], filehash)

        self.litecursor.execute(u'UPDATE Files SET filepath=?, published=?, title=?, title_jpn=?, category=?, tags=?, new=? WHERE hash =?', values)
        self.liteconnection.commit()
        
    def removeFile(self, filehash):
        query = "DELETE FROM Files WHERE hash='"+filehash+"'"
        logger.debug('SQLite delete query: '+query)
        
        self.litecursor.execute(query)
        self.liteconnection.commit()
