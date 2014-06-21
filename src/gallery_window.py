# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gallery_manager import GalleryManager

class GalleryWindow(QMainWindow):
    def __init__(self, gallerypath):
        self.manager = GalleryManager(gallerypath)
        
        QMainWindow.__init__(self)   
        self.resize(800, 500)
        self.initUI()        
        
        self.load_file_list()
    
    def initUI(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.ui_gridLayout = QGridLayout()
        self.ui_gridLayout.setSpacing(15)
        
        # status bar
        self.statusBar().showMessage('Ready')
        
        # menubar
        exitAction = QtGui.QAction(QIcon.fromTheme("application-exit"), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.closeEvent)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        searchMenu = menubar.addMenu('&Search')
        #searchMenu.addAction(exitAction)
        
        # TODO - Use QTreeWidget, hide the header and disable root decoration. 
        self.ui_filelist = QTreeWidget()
        self.ui_filelist.setColumnCount(3)
        self.ui_filelist.itemPressed.connect(self.list_item_pressed)
        self.ui_gridLayout.addWidget(self.ui_filelist, 0, 0, 1, 1)
        
        self.ui_info = QLabel()
        self.ui_gridLayout.addWidget(self.ui_info, 0, 1, 1, 1)

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
        
    # TODO - open details in right widget
    def list_item_pressed(self, treeItem):
        filehash = str(treeItem.text(0))
        logger.debug('Getting info for gallery - '+filehash)
        fileinfo = self.manager.get_file_by_hash(filehash)
        
        self.ui_info.setText(str(fileinfo))
        
    def load_file_list(self):
        """
        Displays all data from database in list
        """
        files = self.manager.get_files()
        
        for f in files:
            treeItem = QTreeWidgetItem(self.ui_filelist)
            treeItem.setText(0, f[0])
            treeItem.setText(1, f[1])
            treeItem.setText(2, f[2])
