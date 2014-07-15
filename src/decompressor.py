# ! /usr/bin/python
# -*- coding: utf-8 -*-

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
        if self.extension == '7z':
            outfile = open(os.path.join(path, file_to_ext), 'wb')
            outfile.write(self.archive.getmember(file_to_ext).read())
            outfile.close()
            self.open_7z.close()
        elif self.extension in ['zip', 'rar']:
            self.archive.extract(file_to_ext, path)
            self.archive.close()
    
    def close(self):
        if self.extension == '7z':
            self.archive.close()
            self.open_7z.close()
        elif self.extension in ['zip', 'rar']:
            self.archive.close()

