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
        super(GalleryWindow, self).__init__()
        self.gallerypath = gallerypath
        self.manager = GalleryManager(self.gallerypath)
        self.selectedFile = None
        
        QMainWindow.__init__(self)   
        self.resize(800, 500)
        self.initUI()        
        
        self.ui_searchbar.setText('')
        self.search()
    
    def initUI(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.ui_layout = QVBoxLayout()
        
        # status bar
        self.statusBar().showMessage('Ready')
        
        # menubar
        menubar = self.menuBar()
        
        exitAction = QtGui.QAction(QIcon.fromTheme("application-exit"), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.closeEvent)
        
        addFileAction = QtGui.QAction(QIcon.fromTheme("document-new"), '&Add file', self)
        addFileAction.setShortcut('Ctrl+A')
        addFileAction.setStatusTip('Add new file information to database')
        addFileAction.triggered.connect(self.addFile)
        
        updateFileAction_API = QtGui.QAction(QIcon.fromTheme("network-wireless"), '&Info from URL (API)', self) 
        updateFileAction_API.setStatusTip('Updates files info with information from URL link (API)')
        updateFileAction_API.triggered.connect(self.updateInfoFromLink_API)
        
        updateFileAction_HTML = QtGui.QAction(QIcon.fromTheme("network-wireless"), '&Info from URL (HTML)', self) 
        updateFileAction_HTML.setStatusTip('Updates files info with information from URL link (HTML parser)')
        updateFileAction_HTML.triggered.connect(self.updateInfoFromLink_HTML)
        
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(addFileAction)
        fileMenu.addAction(updateFileAction_API)
        fileMenu.addAction(updateFileAction_HTML)
        fileMenu.addAction(exitAction)
        
        helpMenu = menubar.addMenu('&Help')
        
        # Search bar
        self.layout_search = QHBoxLayout()
        self.layout_search.setSpacing(5)
        
        self.ui_searchbar = QLineEdit()
        self.ui_searchbar.returnPressed.connect(self.search)
        self.ui_searchbutton = QPushButton('Apply Filter')
        self.ui_searchbutton.pressed.connect(self.search)
        self.ui_clearbutton = QPushButton('Clear Filter')
        self.ui_clearbutton.pressed.connect(self.clearSearch)
        
        self.layout_search.addWidget(self.ui_searchbar)
        self.layout_search.addWidget(self.ui_searchbutton)
        self.layout_search.addWidget(self.ui_clearbutton)
        
        self.ui_layout.addLayout(self.layout_search)
        
        # File list
        self.ui_filelist = QTreeWidget()
        self.ui_filelist.setColumnCount(2)
        colNames = QStringList()
        colNames.append("MD5 Hash")
        colNames.append("Category")
        colNames.append("Title")
        self.ui_filelist.setHeaderLabels(colNames)
        self.ui_filelist.hideColumn(0) # hide column with hashes
        self.ui_filelist.resizeColumnToContents(1) # set category to min width
        
        self.ui_filelist.itemPressed.connect(self.selectFile)
        self.ui_filelist.itemDoubleClicked.connect(self.openFileInReader)
        
        self.ui_layout.addWidget(self.ui_filelist, 1)
        
        # File details 
        self.layout_info = QVBoxLayout()
        
        self.ui_info_title = QLabel()
        self.ui_info_title_jpn = QLabel()
        self.ui_info_category = QLabel()
        self.ui_info_tags = QLabel()
        self.ui_info_filename = QLabel()
        self.ui_info_hash = QLabel()
        
        self.ui_info_title.setWordWrap(True)
        self.ui_info_title_jpn.setWordWrap(True)
        self.ui_info_category.setWordWrap(True)
        self.ui_info_tags.setWordWrap(True)
        self.ui_info_filename.setWordWrap(True)
        self.ui_info_hash.setWordWrap(True)
        
        self.layout_info.addWidget(self.ui_info_title)
        self.layout_info.addWidget(self.ui_info_title_jpn)
        self.layout_info.addWidget(self.ui_info_category)
        self.layout_info.addWidget(self.ui_info_tags)
        self.layout_info.addWidget(self.ui_info_filename)
        self.layout_info.addWidget(self.ui_info_hash)
        self.layout_info.addStretch()
        
        self.ui_layout.addLayout(self.layout_info)
        
        # add layout to main window
        cw.setLayout(self.ui_layout)
        self.setWindowTitle('Man2 - Manga Manager')
        self.show()
        
    def closeEvent(self, event):
        """
        Runs when user tries to close main window.
        """
        self.manager.close()
        QtCore.QCoreApplication.instance().quit()
        
    
    def updateInfoFromLink_API(self):    
        self.updateInfoFromLink(api=True)
        
    def updateInfoFromLink_HTML(self): 
        self.updateInfoFromLink(api=False)
    
    def updateInfoFromLink(self, api=False):
        """
        Updates files info with information from URL link.
        """
        if self.selectedFile is None:
            logger.debug('No file selected, nothing to update.')
            QMessageBox.information(self, 'Message', 'No file selected, nothing to update.')
        else:
            url = QInputDialog.getText(self, 'Update file info from url', 'Enter ehentai.org gallery link:')
            if url[1] == True:
                self.manager.updateFileInfoEHentai(self.selectedFile, str(url[0]), api)
                self.search()
        
    def selectFile(self, treeItem):
        """
        When user clicks on item in list
        """
        self.selectedFile = str(treeItem.text(0))
        self.showFileDetails()
        
    def showFileDetails(self):
        """
        Display info for selected file
        """
        if self.selectedFile is None:
            logger.debug('No file selected, nothing to display.')
            
            self.ui_info_title.setText('')
            self.ui_info_title_jpn.setText('')
            self.ui_info_category.setText('')
            self.ui_info_tags.setText('')
            self.ui_info_filename.setText('')
            self.ui_info_hash.setText('')
        else:
            logger.debug('Display info for -> '+self.selectedFile)
            fileinfo = self.manager.getFileByHash(self.selectedFile)[0]
            
            self.ui_info_title.setText('Title: '+fileinfo['title'])
            self.ui_info_title_jpn.setText('Title [Jpn]: '+fileinfo['title_jpn'])
            self.ui_info_category.setText('Category: '+fileinfo['category'])
            self.ui_info_tags.setText('Tags: '+str(fileinfo['tags']))
            self.ui_info_filename.setText('Filepath: '+fileinfo['filepath'])
            self.ui_info_hash.setText('Hash: '+fileinfo['hash'])
        
    def openFileInReader(self, treeItem):
        """
        When user double clicks on item in list run external manga viewer (mcomix).
        """
        logger.debug('Opening file in external reader.')
        filehash = str(treeItem.text(0))
        filepath_rel = self.manager.getFileByHash(filehash)[0]['filepath']
        filepath = os.path.join(self.gallerypath, filepath_rel)
        
        os.system('mcomix "'+str(filepath)+'"')
        
    def addFile(self):
        """
        Gui for adding new file to database
        """
        logger.debug('gui for adding new file to database')
        
        newfilepath = QFileDialog.getOpenFileName(
                caption='Select Data File',
                directory=self.gallerypath
            )
            
        if (newfilepath is not None) and (newfilepath != ''):
            newfilepath = str(newfilepath).encode("utf8")
            self.manager.addFile(newfilepath)
            self.ui_searchbar.setText('')
            self.search()
        else:
            logger.debug('No filepath selected')
            
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
            treeItem.setText(0, f['hash'])
            treeItem.setText(1, f['category'])
            treeItem.setText(2, f['title'])
        
        self.selectedFile = None
        self.showFileDetails()
        
    def clearSearch(self):
        """
        Displays list of all files in database
        """
        self.ui_searchbar.setText('')
        self.search()
