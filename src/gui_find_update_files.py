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

import sys
import time

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui_eh_update_dialog import EHUpdateDialog

class FindNewDialog(QDialog):
    def __init__(self, manager, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.manager = manager
        self.filelist = []
        
        self.initUI()
        
        self.resize(700, 200)
        
        self.addInfo('Ready')
        
    def initUI(self):
        self.setWindowTitle('Find new files')
        
        layout_main = QVBoxLayout()
        layout_main.setSpacing(5)
        
        ## Info
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setLineWrapMode(QTextEdit.NoWrap)
        
        layout_main.addWidget(self.info, 1)
        
        ## Buttons
        layout_btn = QHBoxLayout()
        layout_btn.setSpacing(5)
        
        self.btn_find = QPushButton('Find new files')
        self.btn_find.pressed.connect(self.findNewFiles)
        self.btn_add = QPushButton('Add new files to database')
        self.btn_add.pressed.connect(self.addNewFiles)
        self.btn_add.setEnabled(False)
        self.btn_update = QPushButton('Update info from EH')
        self.btn_update.pressed.connect(self.updateNewFiles)
        self.btn_update.setEnabled(False)
        self.btn_exit = QPushButton('Exit')
        self.btn_exit.pressed.connect(self.accept)
        
        layout_btn.addStretch()
        layout_btn.addWidget(self.btn_find)
        layout_btn.addWidget(self.btn_add)
        layout_btn.addWidget(self.btn_update)
        layout_btn.addWidget(self.btn_exit)
        layout_btn.addStretch()
        
        layout_main.addLayout(layout_btn)
        
        ## Setup layout
        self.setLayout(layout_main)
        self.show()
        
    def addInfo(self, s='testing printing...'):
        s+='\n'
        self.info.moveCursor(QTextCursor.End)
        self.info.insertPlainText(s)
        
        sb = self.info.verticalScrollBar()
        sb.setValue(sb.maximum())
        
        QtCore.QCoreApplication.processEvents()
        QtCore.QCoreApplication.processEvents()
    
    def findNewFiles(self):
        self.addInfo('Searching for new files... (getting hashes)')
        
        filelist_all = self.manager.getFileList()
        
        self.filelist = []
        for f in filelist_all:
            if f[2] is False:
                self.filelist.append(f)
        
        self.addInfo('Found '+str(len(self.filelist))+' new files')
        
        self.btn_find.setEnabled(False)
        if len(self.filelist) > 0:
            self.btn_add.setEnabled(True)
    
    def addNewFiles(self):
        self.addInfo('Adding new files to database...')
        
        added = self.manager.addFiles(self.filelist, new=True)
        
        self.addInfo('Added '+str(added)+' new files to database')
        
        self.btn_add.setEnabled(False)
        self.btn_update.setEnabled(True)
    
    def updateNewFiles(self):
        self.addInfo('Updating new files with info from EH...')
        
        
        self.addInfo('Requesting lists of galleries...')
        files_galleries = []
        for i in range(len(self.filelist)):
            self.addInfo('Processing '+str(i+1)+'/'+str(len(self.filelist)))
            
            # get information from EH at slower speed == trying to not get ban
            time.sleep(self.manager.getSettings()['eh_delay'])
            
            fileinfo = self.filelist[i]
            if type(fileinfo) == type([]):
                fileinfo = self.manager.getFileByHash(fileinfo[1])[0]
                
            err = 1
            while err==1:
                gallerylist, err = self.manager.findFileOnEH(fileinfo['hash'])
                if err==1:
                    wait = self.manager.getSettings()['eh_overload_delay']
                    self.addInfo('EH connection overloaded, waiting '+str(wait)+'s...')
                    time.sleep(wait)
                    
            if err%10==0 and len(gallerylist) == 0:
                self.addInfo('No info found for: '+fileinfo['filepath'])
                continue
            elif err%10==0:
                files_galleries.append([fileinfo, gallerylist])
            
            if self.printError(err):
                return
            
        self.addInfo('Selecting galleries to update info from...')
        files_galleries_filtered = []
        for i in range(len(files_galleries)):
            fileinfo = files_galleries[i][0]
            gallerylist = files_galleries[i][1]
            
            self.addInfo('Processing '+str(i+1)+'/'+str(len(files_galleries)))
            
            app = EHUpdateDialog(fileinfo, gallerylist, parent=self)
            app.exec_()
            returned = app.getClicked()
            if returned is not None:
                files_galleries_filtered.append([fileinfo, returned[3]])
        
        self.addInfo('Updating selected galleries from EH...')
        for i in range(len(files_galleries_filtered)):
            self.addInfo('Processing '+str(i+1)+'/'+str(len(files_galleries_filtered)))
            
            # get information from EH at slower speed == trying to not get ban
            time.sleep(self.manager.getSettings()['eh_delay'])
            
            fileinfo = files_galleries_filtered[i][0]
            url = files_galleries_filtered[i][1]
            
            err = 1
            while err==1:
                err = self.manager.updateFileInfoEHentai(fileinfo['hash'], str(url))
                if err==1:
                    wait = self.manager.getSettings()['eh_overload_delay']
                    self.addInfo('EH connection overloaded, waiting '+wait+'s...')
                    time.sleep(wait)
                    
            if self.printError(err):
                return
                
        self.addInfo('Finished!!!')
        
        self.btn_update.setEnabled(False)
        
    def printError(self, err):
        """
        returns True if process should terminate
        """
        r = False
        
        if err==2:
            self.addInfo('Banned on EH. Terminating process...')
            r = True
        elif err==3:
            self.addInfo('Undefined error on EH. Terminating process...')
            r = True
        elif err==20:
            self.addInfo('HTML failed, using API (cant get namespaces)')
        elif err==21:
            self.addInfo('HTML failed, API error')
        elif err==31:
            self.addInfo('Image hash couldnt be generated')
        elif err%10!=0:
            self.addInfo('Returned error code: '+str(err))
            
        return r
        
class UpdateSearchDialog(FindNewDialog):
    def __init__(self, manager, filelist, parent=None):
        FindNewDialog.__init__(self, manager, parent)

        self.filelist = filelist
        self.addInfo('Loaded '+str(len(self.filelist))+' files to be updated')
        
        self.btn_find.setEnabled(False)
        self.btn_add.setEnabled(False)
        self.btn_update.setEnabled(True)


# Testing layout
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fnd = FindNewDialog(None)
    sys.exit(app.exec_())
        
