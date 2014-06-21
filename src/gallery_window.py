# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys

from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gallery_manager import GalleryManager

class GalleryWindow(QMainWindow):
    def __init__(self, gallerypath):
        self.manager = GalleryManager(gallerypath)
        
        QMainWindow.__init__(self)   
        self.initUI()
    
    def initUI(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.ui_gridLayout = QGridLayout()
        self.ui_gridLayout.setSpacing(15)
        
        # status bar
        self.statusBar().showMessage('Ready')

        rstart = 0
        
        #self.ui_helpWidget = None
        #self.ui_helpWidget_pos = rstart
        #self.ui_embeddedAppWindow = QLabel('Default window')  
        #self.ui_embeddedAppWindow_pos = rstart + 1
        
        #self.ui_gridLayout.addWidget(self.ui_embeddedAppWindow, rstart + 1, 1)
        #rstart +=2

        cw.setLayout(self.ui_gridLayout)
        self.setWindowTitle('Man2 - Manga Manager')
        self.show()
        
    def closeEvent(self, event):
        """
        Runs when user tryes to close main window.
        sys.exit(0) - to fix wierd bug, where process is not terminated.
        """
        self.manager.close()
        sys.exit(0)
