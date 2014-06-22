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
        self.gallerypath = gallerypath
        self.manager = GalleryManager(self.gallerypath)
        
        QMainWindow.__init__(self)   
        self.resize(800, 500)
        self.initUI()        
        
        self.ui_searchbar.setText('')
        self.search()
    
    def initUI(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.ui_layout = QVBoxLayout()
        self.ui_layout.setSpacing(5)
        
        # status bar
        self.statusBar().showMessage('Ready')
        
        # menubar
        menubar = self.menuBar()
        
        exitAction = QtGui.QAction(QIcon.fromTheme("application-exit"), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.closeEvent)
        
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        searchMenu = menubar.addMenu('&Edit')
        
        helpMenu = menubar.addMenu('&Help')
        
        # Search bar
        self.layout_search = QHBoxLayout()
        self.layout_search.setSpacing(5)
        
        self.ui_searchbar = QLineEdit()
        self.ui_searchbar.returnPressed.connect(self.search)
        self.ui_searchbutton = QPushButton('Search')
        self.ui_searchbutton.pressed.connect(self.search)
        
        self.layout_search.addWidget(self.ui_searchbar)
        self.layout_search.addWidget(self.ui_searchbutton)
        
        self.ui_layout.addLayout(self.layout_search)
        
        # File list and details layout
        self.layout_main = QHBoxLayout()
        self.layout_main.setSpacing(15)
        
        # File list
        self.ui_filelist = QTreeWidget()
        self.ui_filelist.setColumnCount(4)
        colNames = QStringList()
        colNames.append("MD5 Hash")
        colNames.append("Title")
        colNames.append("Title [Jpn]")
        colNames.append("Category")
        colNames.append("Tags")
        self.ui_filelist.setHeaderLabels(colNames)
        self.ui_filelist.hideColumn(0) # hide column with hashes
        self.ui_filelist.itemPressed.connect(self.show_file_details)
        self.ui_filelist.itemDoubleClicked.connect(self.open_file_in_reader)
        self.layout_main.addWidget(self.ui_filelist)
        
        # File details 
        self.layout_info = QVBoxLayout()
        self.layout_info.setSpacing(5)
        
        self.ui_info_name_eng = QLabel()
        self.ui_info_name_jp = QLabel()
        self.ui_info_category = QLabel()
        self.ui_info_tags = QLabel()
        self.ui_info_filename = QLabel()
        self.ui_info_hash = QLabel()
        
        self.layout_info.addWidget(self.ui_info_name_eng)
        self.layout_info.addWidget(self.ui_info_name_jp)
        self.layout_info.addWidget(self.ui_info_category)
        self.layout_info.addWidget(self.ui_info_tags)
        self.layout_info.addWidget(self.ui_info_filename)
        self.layout_info.addWidget(self.ui_info_hash)
        self.layout_info.addStretch()
        
        self.layout_main.addLayout(self.layout_info)
        
        # add layout to main window
        self.ui_layout.addLayout(self.layout_main)
        cw.setLayout(self.ui_layout)
        self.setWindowTitle('Man2 - Manga Manager')
        self.show()
        
    def closeEvent(self, event):
        """
        Runs when user tryes to close main window.
        sys.exit(0) - to fix wierd bug, where process is not terminated.
        """
        self.manager.close()
        sys.exit(0)
        
    def show_file_details(self, treeItem):
        """
        When user clicks on item in list
        """
        filehash = str(treeItem.text(0))
        logger.debug('Display info for -> '+filehash)
        fileinfo = self.manager.get_file_by_hash(filehash)[0]
        
        self.ui_info_name_eng.setText('Title: '+str(fileinfo[2]))
        self.ui_info_name_jp.setText('Title [Jpn]: '+str(fileinfo[3]))
        self.ui_info_category.setText('Category: '+str(fileinfo[4]))
        self.ui_info_tags.setText('Tags: '+str(fileinfo[5]))
        self.ui_info_filename.setText('Filename: '+str(fileinfo[1]))
        self.ui_info_hash.setText('Hash: '+str(fileinfo[0]))
        
    def open_file_in_reader(self, treeItem):
        """
        When user double clicks on item in list run external manga viewer (mcomix).
        """
        logger.debug('Opening file in external reader.')
        filehash = str(treeItem.text(0))
        filename = self.manager.get_file_by_hash(filehash)[0][1]
        filepath = os.path.join(os.path.join(self.gallerypath, "Files"), filename)
        
        os.system("mcomix "+str(filepath))
        
    # TODO - finish this
    def search(self):
        """
        Displays filtered data from database
        """
        searchstring = str(self.ui_searchbar.text())
        logger.debug('Searching -> '+str(searchstring))
        
        filteredlist = self.manager.search(searchstring)
        
        self.ui_filelist.clear()
        for f in filteredlist:
            treeItem = QTreeWidgetItem(self.ui_filelist)
            treeItem.setText(0, f[0])
            treeItem.setText(1, f[2])
            treeItem.setText(2, f[3])
            treeItem.setText(3, f[4])
            treeItem.setText(4, f[5])

