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
                    'eh_delay': 3,
                    'eh_overload_delay': 60,
                    'categories': ['doujinshi', 'manga', 'artist cg sets', 'game cg sets', 'western', 'non-h', 'image sets',                'cosplay', 'asian porn', 'misc'],
                    'categories_enabled': [],
                    'namespaces': ['language', 'parody', 'character', 'group', 'artist', 'male', 'female', 'misc']
                    }
        return default
