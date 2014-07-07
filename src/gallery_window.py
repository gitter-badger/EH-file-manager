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
        
        
        
        addFileAction = QtGui.QAction(QIcon.fromTheme("document-new"), 'Add file', self)
        addFileAction.setShortcut('Ctrl+A')
        addFileAction.setStatusTip('Add new file information to database')
        addFileAction.triggered.connect(self.addFile)
        
        editFileAction = QtGui.QAction('Edit file', self)
        editFileAction.setShortcut('Ctrl+E')
        editFileAction.setStatusTip('Edit file information')
        editFileAction.triggered.connect(self.editFile)
        
        removeFileAction = QtGui.QAction(QIcon.fromTheme("edit-delete"), 'Remove file', self)
        removeFileAction.setShortcut('Ctrl+R')
        removeFileAction.setStatusTip('Remove file from info database')
        removeFileAction.triggered.connect(self.removeFile)
        
        updateFileAction_API = QtGui.QAction('Info from URL (API)', self) 
        updateFileAction_API.setShortcut('Alt+A')
        updateFileAction_API.setStatusTip('Updates files info with information from URL link (API)')
        updateFileAction_API.triggered.connect(self.updateInfoFromLink_API)
        
        updateFileAction_HTML = QtGui.QAction('Info from URL (HTML)', self) 
        updateFileAction_HTML.setShortcut('Alt+H')
        updateFileAction_HTML.setStatusTip('Updates files info with information from URL link (HTML parser)')
        updateFileAction_HTML.triggered.connect(self.updateInfoFromLink_HTML)

        findNewFilesAction = QtGui.QAction(QIcon.fromTheme("find"), 'Find new files', self)
        findNewFilesAction.setShortcut('Ctrl+F')
        findNewFilesAction.setStatusTip('Automatically find new files in gallery and add them to database')
        findNewFilesAction.triggered.connect(self.findNewFiles)
        
        settingsAction = QtGui.QAction(QIcon.fromTheme("document-properties"), 'Settings', self)
        settingsAction.setShortcut('Ctrl+S')
        settingsAction.setStatusTip('Edit application settings')
        settingsAction.triggered.connect(self.editSettings)
        
        exitAction = QtGui.QAction(QIcon.fromTheme("application-exit"), 'Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.closeEvent)
        
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(addFileAction)
        fileMenu.addAction(editFileAction)
        fileMenu.addAction(removeFileAction)
        fileMenu.addAction(updateFileAction_API)
        fileMenu.addAction(updateFileAction_HTML)
        fileMenu.addAction(findNewFilesAction)
        fileMenu.addAction(settingsAction)
        fileMenu.addAction(exitAction)
        
        helpMenu = menubar.addMenu('Help')
        
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
        self.ui_layout_info = QVBoxLayout()
        self.ui_layout_info.setSpacing(0)
        
        self.ui_info = ShowDetails(self.manager)
        self.ui_layout_info.addWidget(self.ui_info)
        
        self.ui_layout.addLayout(self.ui_layout_info)
        
        # add layout to main window
        cw.setLayout(self.ui_layout)
        self.setWindowTitle('EH file manager')
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
        self.ui_layout_info.removeWidget(self.ui_info)
        self.ui_info.close()
        
        self.ui_info = ShowDetails(self.manager, self.selectedFile)
        
        self.ui_layout_info.addWidget(self.ui_info)
        self.ui_layout_info.update()
        self.ui_layout.update()
        
    def openFileInReader(self, treeItem):
        """
        When user double clicks on item in list run external manga viewer (mcomix).
        """
        logger.debug('Opening file in external reader.')
        filehash = str(treeItem.text(0))
        filepath_rel = str(self.manager.getFileByHash(filehash)[0]['filepath'])
        filepath = os.path.join(self.gallerypath, filepath_rel)
        
        # get path to executable of external archive reader
        reader = self.manager.getSettings()['reader']
        
        # @TODO - open in separate thread (dont wait for it to finish)
        os.system(reader+' "'+str(filepath)+'"')
        
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
            self.search()
        else:
            logger.debug('No filepath selected')
            
    def removeFile(self):
        if self.selectedFile is None:
            logger.debug('No file selected, nothing to remove.')
            QMessageBox.information(self, 'Message', 'No file selected, nothing to remove.')
        else:
            self.manager.removeFile(str(self.selectedFile))
            self.search()
        
    def editFile(self):
        if self.selectedFile is None:
            logger.debug('No file selected, nothing to edit.')
            QMessageBox.information(self, 'Message', 'No file selected, nothing to edit.')
        else:
            # @TODO - block main window when editing
            app = EditDetails(self.manager, str(self.selectedFile))
            app.exec_()
            self.search()
            
    def findNewFiles(self):
        self.statusBar().showMessage('Searching for new files...')
        QMessageBox.information(self, 'Find new files', 'Manager will now try to find new files.')
        
        newfiles = self.manager.addNewFiles()
        
        self.statusBar().showMessage('Ready')
        QMessageBox.information(self, 'Find new files', 'Manager found '+str(newfiles)+' new files.')
        
        self.search()
        
    def editSettings(self):
        # @TODO - block main window when editing
        app = EditSettings(self.manager)
        app.exec_()
            
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
        
class ShowDetails(QDialog):
    def __init__(self, manager, filehash=None):
        self.manager = manager
        self.filehash = filehash
        
        QDialog.__init__(self)
        
        if self.filehash is None or str(self.filehash)=='':
            logger.debug('No file selected, nothing to display.')
            self.fileinfo = None
            self.initUI_E()
        else:
            logger.debug('Display info for -> '+self.filehash)
            self.fileinfo = self.manager.getFileByHash(self.filehash)[0]
            logger.debug(str(self.fileinfo))
            self.initUI()
    
    def initUI(self):
        layout_main = QVBoxLayout()
        layout_main.setSpacing(2)
        
        ## Basic info
        if self.fileinfo['title']!='':
            self.ui_title = QLabel('<b>Title:</b>  '+self.fileinfo['title'])
            self.ui_title.setWordWrap(True)
            layout_main.addWidget(self.ui_title)
            
        if self.fileinfo['title_jpn']!='':
            self.ui_title_jpn = QLabel('<b>Title [Jpn]:</b>  '+self.fileinfo['title_jpn'])
            self.ui_title_jpn.setWordWrap(True)
            layout_main.addWidget(self.ui_title_jpn)
            
        self.ui_category = QLabel('<b>Category:</b>  '+self.fileinfo['category'])
        self.ui_category.setWordWrap(True)
        layout_main.addWidget(self.ui_category)
        
        ## Tags
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        layout_main.addWidget(hr)
        
        # get list of main namespaces from config
        namespaces = self.manager.getSettings()['namespaces']
        
        # standard tag namespaces
        for tc in namespaces:
            if tc in self.fileinfo['tags']:
                tags = QLabel('<b>'+tc+':</b> '+', '.join(self.fileinfo['tags'][tc]))
                tags.setWordWrap(True)
                layout_main.addWidget(tags)
        
        # other non-standard tag namespaces
        for tc in self.fileinfo['tags']:
            if not (tc in namespaces):
                tags = QLabel('<b>'+tc+':</b> '+', '.join(self.fileinfo['tags'][tc]))
                tags.setWordWrap(True)
                layout_main.addWidget(tags)
        
        ## Setup layout
        layout_main.addStretch()
        self.setLayout(layout_main)
        self.show()
        
    def initUI_E(self):
        layout_main = QVBoxLayout()
        self.setLayout(layout_main)
        self.show()
        
class EditDetails(QDialog):
    def __init__(self, manager, filehash):
        self.manager = manager
        self.filehash = filehash
        self.old_fileinfo = self.manager.getFileByHash(self.filehash)[0]
        self.new_fileinfo = {}
        
        QDialog.__init__(self)
        self.initUI()
        
        self.resize(700, 50)
        
    def initUI(self):
        self.setWindowTitle('Edit fileinfo')
        
        layout_main = QGridLayout()
        layout_main.setSpacing(5)
        rstart = 0
        
        ## Fileinfo form - basic
        self.line_title = QLineEdit(self.old_fileinfo['title'])
        self.line_title_jpn = QLineEdit(self.old_fileinfo['title_jpn'])
        self.line_category = QLineEdit(self.old_fileinfo['category'])
        
        layout_main.addWidget(QLabel('<b>Title:</b> '), rstart + 0, 0)
        layout_main.addWidget(self.line_title, rstart + 0, 1)
        layout_main.addWidget(QLabel('<b>Title [Jpn]:</b> '), rstart + 1, 0)
        layout_main.addWidget(self.line_title_jpn, rstart + 1, 1)
        layout_main.addWidget(QLabel('<b>Category:</b> '), rstart + 2, 0)
        layout_main.addWidget(self.line_category, rstart + 2, 1)
        rstart+=3
        
        ## Fileinfo form - tags
        # @TODO - new namespace
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        
        layout_main.addWidget(hr, rstart + 0, 0, 1, 2)
        rstart+=1
        
        # get list of main namespaces from config
        namespaces = self.manager.getSettings()['namespaces']
        
        self.line_tags = {}
        # standard tag namespaces
        for tc in namespaces:
            if tc in self.old_fileinfo['tags']:
                self.line_tags[tc] = QLineEdit(', '.join(self.old_fileinfo['tags'][tc]))
            else:
                self.line_tags[tc] = QLineEdit()
                
            layout_main.addWidget(QLabel('<b>'+str(tc)+':</b> '), rstart + 0, 0)
            layout_main.addWidget(self.line_tags[tc], rstart + 0, 1)
            rstart+=1
        
        # other non-standard tag namespaces
        for tc in self.old_fileinfo['tags']:
            if not (tc in namespaces):
                self.line_tags[tc] = QLineEdit(', '.join(self.old_fileinfo['tags'][tc]))
                
                layout_main.addWidget(QLabel('<b>'+str(tc)+':</b> '), rstart + 0, 0)
                layout_main.addWidget(self.line_tags[tc], rstart + 0, 1)
                rstart+=1
        
        ## Buttons
        hr3 = QFrame()
        hr3.setFrameShape(QFrame.HLine)
        
        btn_close = QPushButton('Cancel')
        btn_close.pressed.connect(self.close)
        btn_edit = QPushButton('Edit')
        btn_edit.pressed.connect(self.edit)
        
        layout_main.addWidget(hr3, rstart + 0, 0, 1, 2)
        layout_main.addWidget(btn_close, rstart + 1, 0)
        layout_main.addWidget(btn_edit, rstart + 1, 1)
        rstart+=2
        
        ## Stretcher
        layout_main.addItem(QSpacerItem(0,0), rstart + 0, 0)
        layout_main.setRowStretch(rstart + 0, 1)
        rstart+=1
        
        ## Setup layout
        self.setLayout(layout_main)
        self.show()
    
    def edit(self):
        self.new_fileinfo = dict(self.old_fileinfo)
        
        self.new_fileinfo['title'] = self.line_title.text()
        self.new_fileinfo['title_jpn'] = self.line_title_jpn.text()
        self.new_fileinfo['category'] = str(self.line_category.text()).lower()
        
        self.new_fileinfo['tags'] = {}
        for tc in self.line_tags:
            if str(self.line_tags[tc].text()).strip() != '':
                t_list = [t.strip() for t in str(self.line_tags[tc].text()).lower().split(',')]
                self.new_fileinfo['tags'][tc] = t_list
        
        self.manager.updateFileInfo(self.filehash, self.new_fileinfo)
        self.close()
        
class EditSettings(QDialog):
    def __init__(self, manager):
        self.manager = manager
        self.old_settings = self.manager.getSettings()
        self.new_settings = {}
        
        QDialog.__init__(self)
        self.initUI()
        
        self.resize(700, 50)
        
    def initUI(self):
        self.setWindowTitle('Edit settings')
        
        layout_main = QGridLayout()
        layout_main.setSpacing(5)
        rstart = 0
        
        ## Fileinfo form - basic
        self.line_reader = QLineEdit(self.old_settings['reader'])
        self.line_categories = QLineEdit(', '.join(self.old_settings['categories']))
        self.line_namespaces = QLineEdit(', '.join(self.old_settings['namespaces']))
        
        layout_main.addWidget(QLabel('<b>Reader:</b> '), rstart + 0, 0)
        layout_main.addWidget(self.line_reader, rstart + 0, 1)
        layout_main.addWidget(QLabel('<b>Categories:</b> '), rstart + 1, 0)
        layout_main.addWidget(self.line_categories, rstart + 1, 1)
        layout_main.addWidget(QLabel('<b>Namespaces:</b> '), rstart + 2, 0)
        layout_main.addWidget(self.line_namespaces, rstart + 2, 1)
        rstart+=3
        
        ## Buttons
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        
        btn_close = QPushButton('Cancel')
        btn_close.pressed.connect(self.close)
        btn_edit = QPushButton('Edit')
        btn_edit.pressed.connect(self.edit)
        
        layout_main.addWidget(hr, rstart + 0, 0, 1, 2)
        layout_main.addWidget(btn_close, rstart + 1, 0)
        layout_main.addWidget(btn_edit, rstart + 1, 1)
        rstart+=2
        
        ## Stretcher
        layout_main.addItem(QSpacerItem(0,0), rstart + 0, 0)
        layout_main.setRowStretch(rstart + 0, 1)
        rstart+=1
        
        ## Setup layout
        self.setLayout(layout_main)
        self.show()
        
    def edit(self):
        self.new_settings = dict(self.old_settings)
        
        self.new_settings['reader'] = str(self.line_reader.text())
        
        self.new_settings['categories'] = [x.strip() for x in str(self.line_categories.text()).lower().split(',')]
        self.new_settings['namespaces'] = [x.strip() for x in str(self.line_namespaces.text()).lower().split(',')]
        
        self.manager.saveSettings(self.new_settings)
        self.close()
        
        
