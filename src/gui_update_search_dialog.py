# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import sys
import time

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
        self.btn_exit.setEnabled(False)
        QtCore.QCoreApplication.processEvents()
        QtCore.QCoreApplication.processEvents()
        
        for f in self.filelist:
            # get information from EH at slower speed == trying to not get ban
            time.sleep(4)
            
            err = 1
            while err==1:
                gallerylist, err = self.manager.findFileOnEH(f['hash'])
                if err==1:
                    self.addInfo('EH connection overloaded, waiting 60s...')
                    QtCore.QCoreApplication.processEvents()
                    time.sleep(60)

            if err==0 and len(gallerylist) == 0:
                self.addInfo('No info found for: '+f['filepath'])
                QtCore.QCoreApplication.processEvents()
                continue
                
            if err==0:
                app = EHUpdateDialog(f, gallerylist, parent=self)
                app.exec_()
                returned = app.getClicked()
                if returned is not None:
                    eh_gallery = returned[3]
                    
                    err = 1
                    while err==1:
                        err = self.manager.updateFileInfoEHentai(f['hash'], str(eh_gallery))
                        if err==1:
                            self.addInfo('EH connection overloaded, waiting 60s...')
                            QtCore.QCoreApplication.processEvents()
                            time.sleep(60)
                
            if err==2:
                self.addInfo('Banned on EH. Terminating process...')
                QtCore.QCoreApplication.processEvents()
                break
            elif err==3:
                self.addInfo('Undefined error on EH. Terminating process...')
                QtCore.QCoreApplication.processEvents()
                break
            elif err==20:
                self.addInfo('HTML failed, using API (cant get namespaces)')
                QtCore.QCoreApplication.processEvents()
            elif err==21:
                self.addInfo('API error')
                QtCore.QCoreApplication.processEvents()
            elif err!=0:
                self.addInfo('Returned error code: '+str(err))
                QtCore.QCoreApplication.processEvents()
                
        self.addInfo('Finished!!!')
        
        self.btn_exit.setEnabled(True)
        self.btn_update.setEnabled(False)


# Testing layout
if __name__ == "__main__":
    app = QApplication(sys.argv)
    usd = UpdateSearchDialog(None, [])
    sys.exit(app.exec_())
