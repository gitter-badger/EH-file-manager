# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import yaml

class Settings():
    FILENAME = 'settings.yaml'
    
    def __init__(self, configpath):
        self.settingspath = os.path.join(configpath, self.FILENAME)
        
        self.settings = None
        
    def getSettings(self):
        return self.settings
        
    def setSettings(self, newsettings):
        logger.debug('Loading new settings')
        self.settings = newsettings
        
    def loadSettings(self, path=None):
        if path is None:
            path = self.settingspath
        
        self.settings = self.getDefaultSettings()
        
        if self.hasSettings(path):
            logger.debug('Loading existing settings')
            f = open(path, 'rb')
            self.settings.update(yaml.load(f))
            f.close()
        else:
            logger.debug('Using default settings')
    
    def saveSettings(self):
        if self.settings is None:
            logger.error('No settings to write')
        else:
            logger.debug('Saving settings to file')
            f = open(self.settingspath, 'wb')
            yaml.dump(self.settings, f)
            f.close
        
    # @TODO - check for all needed parameters
    def hasSettings(self, path = None):
        """
        Returns:
            True - Path has settings file in correct format
            False - No file or file in bad format
        """
        if path is None:
            path = self.settingspath
        
        try:
            f = open(path, 'rb')
            yaml.load(f)
            f.close()
        except:
            logger.warning('Bad settings file/path!!!')
            return False
        
        return True
    
    def getDefaultSettings(self):
        default = {
                    'reader': 'mcomix',
                    'allowed_extensions': ['zip', '7z', 'rar'],
                    'categories': ['doujinshi', 'manga', 'artist cg sets', 'game cg sets', 'western', 'non-h', 'image sets',                'cosplay', 'asian porn', 'misc'],
                    'categories_enabled': [],
                    'namespaces': ['language', 'parody', 'character', 'group', 'artist', 'male', 'female', 'misc']
                    }
        return default
