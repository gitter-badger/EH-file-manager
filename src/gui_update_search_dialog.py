# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui_eh_update_dialog import EHUpdateDialog

class UpdateSearchDialog(QDialog):
    def __init__(self, manager, filelist, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.manager = manager
        self.filelist = filelist
        
        self.initUI()
        
        self.resize(700, 200)
        
        self.addInfo('Loaded '+str(len(self.filelist))+' files to be updated')
        self.addInfo('Ready')
        
    def initUI(self):
        self.setWindowTitle('Update search results')
        
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
        
        self.btn_update = QPushButton('Update info from EH')
        self.btn_update.pressed.connect(self.updateFiles)
        self.btn_exit = QPushButton('Exit')
        self.btn_exit.pressed.connect(self.accept)
        
        layout_btn.addStretch()
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
    
    def updateFiles(self):
        self.addInfo('Updating files with info from EH...')
        QtCore.QCoreApplication.processEvents()
        
        for f in self.filelist:
            gallerylist = self.manager.findFileOnEH(f['hash'])
            if len(gallerylist) == 0:
                self.addInfo('No info found for: '+f['filepath'])
                QtCore.QCoreApplication.processEvents()
                continue
            app = EHUpdateDialog(f, gallerylist, parent=self)
            app.exec_()
            returned = app.getClicked()
            if returned is not None:
                eh_gallery = returned[3]
                self.manager.updateFileInfoEHentai(f['hash'], str(eh_gallery))
                
        self.addInfo('Finished!!!')
        
        self.btn_update.setEnabled(False)


# Testing layout
if __name__ == "__main__":
    app = QApplication(sys.argv)
    usd = UpdateSearchDialog(None, [])
    sys.exit(app.exec_())
