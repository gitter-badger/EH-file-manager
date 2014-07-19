# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import sys

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
    
    def findNewFiles(self):
        self.addInfo('Searching for new files... (getting hashes)')
        QtCore.QCoreApplication.processEvents()
        
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
        QtCore.QCoreApplication.processEvents()
        
        added = self.manager.addFiles(self.filelist, new=True)
        
        self.addInfo('Added '+str(added)+' new files to database')
        
        self.btn_add.setEnabled(False)
        self.btn_update.setEnabled(True)
    
    def updateNewFiles(self):
        self.addInfo('Updating new files with info from EH...')
        QtCore.QCoreApplication.processEvents()
        
        for f in self.filelist:
            gallerylist = self.manager.findFileOnEH(f[1])
            fileinfo = self.manager.getFileByHash(f[1])[0]
            if len(gallerylist) == 0:
                self.addInfo('No info found for: '+fileinfo['filepath'])
                QtCore.QCoreApplication.processEvents()
                continue
            app = EHUpdateDialog(fileinfo, gallerylist, parent=self)
            app.exec_()
            returned = app.getClicked()
            if returned is not None:
                eh_gallery = returned[3]
                self.manager.updateFileInfoEHentai(f[1], str(eh_gallery))
                
        self.addInfo('Finished!!!')
        
        self.btn_update.setEnabled(False)


# Testing layout
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fnd = FindNewDialog(None)
    sys.exit(app.exec_())
        
