# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys

import yaml

class Settings():
    def __init__(self, configpath):
        self.settingsfile='settings.yaml'
        self.settingspath = os.path.join(configpath, self.settingsfile)
        
        self.settings = None
        
    def getSettings(self):
        return self.settings
        
    def setSettings(self, newsettings):
        logger.debug('Loading new settings')
        self.settings = newsettings
        
    def loadSettings(self, path=None):
        if path is None:
            path = self.settingspath
        
        if self.hasSettings(path):
            logger.debug('Loading existing settings')
            f = open(path, 'rb')
            self.settings = yaml.load(f)
            f.close()
        else:
            logger.debug('Using default settings')
            self.settings = self.getDefaultSettings()
    
    def saveSettings(self):
        if self.settings is None:
            logger.error('No settings to write')
        else:
            logger.error('Saving settings to file')
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
            obj = yaml.load(f)
            f.close()
        except:
            logger.warning('Bad settings file/path!!!')
            return False
        
        return True
    
    def getDefaultSettings(self):
        # @TODO - check if I wrote them right + if is nothing missing 
        default = {
                    'reader': 'mcomix',
                    'categories': ['manga', 'doujinshi', 'non-h', 'western', 'imageset', 'artistcg', 'misc'],
                    'namespaces': ['language', 'parody', 'character', 'group', 'artist', 'male', 'female', 'misc']
                    }
        return default
