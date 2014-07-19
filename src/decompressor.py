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

import py7zlib
import rarfile
import zipfile
    
class ArchiveFile():
    def __init__(self, filepath):
        self.extension = filepath.lower().split('.')[-1]
        self.open_7z = None
        
        if self.extension == '7z':
            self.open_7z = open(filepath, 'rb')
            self.archive = py7zlib.Archive7z(self.open_7z)
        elif self.extension == 'zip':
            self.archive = zipfile.ZipFile(filepath)
        elif self.extension == 'rar':
            self.archive = rarfile.RarFile(filepath)
        else:
            logger.error('Unsupported file format')
            raise TypeError
            
    def namelist(self):
        if self.extension == '7z':
            filelist = self.archive.getnames()
        elif self.extension == 'zip':
            filelist = self.archive.namelist()
        elif self.extension == 'rar':
            filelist = self.archive.namelist()
            
        return filelist
        
    def extract(self, file_to_ext, path):
        """
        Extracts one file from archive to given path
        """
        if type(path) == type(u''):
            path = path.encode('utf-8')
        
        if self.extension == '7z':
            outfile_name = 'img.'+file_to_ext.split('.')[-1]
            outfile = open(os.path.join(path, outfile_name), 'wb')
            outfile.write(self.archive.getmember(file_to_ext).read())
            outfile.close()
            self.open_7z.close()
        elif self.extension in ['zip', 'rar']:
            self.archive.extract(file_to_ext, path)
            self.archive.close()
    
    def close(self):
        if self.extension == '7z':
            self.open_7z.close()
        elif self.extension in ['zip', 'rar']:
            self.archive.close()

