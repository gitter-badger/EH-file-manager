# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import sys
import thread
import datetime

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gallery_manager import GalleryManager
from eh_update_dialog import EHUpdateDialog

class GalleryWindow(QMainWindow):
    def __init__(self, gallerypath):
        QMainWindow.__init__(self)
        
        self.gallerypath = unicode(gallerypath)
        self.manager = GalleryManager(self.gallerypath)
        self.selectedFile = None
        
        QMainWindow.__init__(self)   
        self.resize(1000, 700)
        self.initUI()        
        
        self.ui_searchbar.setText('')
        self.search()
    
    def initUI(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        self.ui_layout = QVBoxLayout()
        
        # status bar
        self.statusBar().showMessage('Ready')
        
        ## Menubar
        menubar = self.menuBar() 
        
        # File menu
        addFileAction = QtGui.QAction(QIcon.fromTheme("document-new"), 'Add file', self)
        addFileAction.setShortcut('Ctrl+A')
        addFileAction.setStatusTip('Add new file information to database')
        addFileAction.triggered.connect(self.addFile)
        
        findNewFilesAction = QtGui.QAction(QIcon.fromTheme("find"), 'Find new files', self)
        findNewFilesAction.setShortcut('Ctrl+F')
        findNewFilesAction.setStatusTip('Automatically find new files in gallery and add them to database')
        findNewFilesAction.triggered.connect(self.findNewFiles)
        
        updateNewFilesEHAction = QtGui.QAction('Update new files EH', self)
        updateNewFilesEHAction.setStatusTip('Automatically updates info of new files with information from EH')
        updateNewFilesEHAction.triggered.connect(self.updateNewFilesFromEH)
        
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
        fileMenu.addAction(findNewFilesAction)
        fileMenu.addAction(updateNewFilesEHAction)
        fileMenu.addAction(settingsAction)
        fileMenu.addAction(exitAction)
        
        # Edit menu
        openFileAction = QtGui.QAction('Open in reader', self)
        openFileAction.setShortcut('Ctrl+O')
        openFileAction.setStatusTip('Open file in external reader')
        openFileAction.triggered.connect(self.openFileInReader)
        
        editFileAction = QtGui.QAction('Edit file', self)
        editFileAction.setShortcut('Ctrl+E')
        editFileAction.setStatusTip('Edit file information')
        editFileAction.triggered.connect(self.editFile)
        
        removeFileAction = QtGui.QAction('Remove file', self)
        removeFileAction.setShortcut('Ctrl+R')
        removeFileAction.setStatusTip('Remove file info from database')
        removeFileAction.triggered.connect(self.removeFile)

        updateFileAction_Link = QtGui.QAction('Info from EH Link', self) 
        updateFileAction_Link.setStatusTip('Updates file info with information from e-hentai.org link (from HTML, API is fallback)')
        updateFileAction_Link.triggered.connect(self.updateInfoFromLink)
        
        updateFileAction_EH = QtGui.QAction('Info from EH', self) 
        updateFileAction_EH.setStatusTip('Updates file info with information from e-hentai.org (automatically finds gallery link)')
        updateFileAction_EH.triggered.connect(self.updateInfoFromEH)
        
        editMenu = menubar.addMenu('Edit')
        editMenu.addAction(openFileAction)
        editMenu.addAction(editFileAction)
        editMenu.addAction(removeFileAction)
        editMenu.addAction(updateFileAction_Link)
        editMenu.addAction(updateFileAction_EH)
        
        ## Help menu
        #helpMenu = menubar.addMenu('Help')
        
        ## Search bar
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
        
        # search - category filter
        self.layout_cat_search = QHBoxLayout()
        self.layout_cat_search.setSpacing(5)
        
        self.ui_btn_categories = []
        for c in self.manager.getSettings()['categories']:
            c_btn = QtGui.QPushButton(c, self)
            c_btn.setCheckable(True)
            
            if self.manager.getSettings()['categories_enabled'] == []:
                c_btn.setChecked(True)
            elif c in self.manager.getSettings()['categories_enabled']:
                c_btn.setChecked(True)
            
            self.ui_btn_categories.append(c_btn)
            self.layout_cat_search.addWidget(c_btn)
        
        self.layout_cat_search.addStretch()
        self.ui_layout.addLayout(self.layout_cat_search)
        
        # advanced search settings
        self.layout_ad_search = QHBoxLayout()
        self.layout_ad_search.setSpacing(5)
        
        self.ui_box_new = QCheckBox('Only new files', self)
        self.ui_box_del = QCheckBox('Only deleted files', self)
        
        sorts = ['published', 'title', 'title_jpn']
        self.ui_combobox_sort = QComboBox()
        self.ui_combobox_sort.addItems(sorts)
            
        selectedIndex = self.ui_combobox_sort.findText(sorts[0])
        self.ui_combobox_sort.setCurrentIndex(selectedIndex)
        
        self.ui_box_sort_rev = QCheckBox('reverse', self)
        
        self.layout_ad_search.addWidget(self.ui_box_new)
        self.layout_ad_search.addWidget(self.ui_box_del)
        self.layout_ad_search.addWidget(QLabel('Sort:'))
        self.layout_ad_search.addWidget(self.ui_combobox_sort)
        self.layout_ad_search.addWidget(self.ui_box_sort_rev)
        
        self.layout_ad_search.addStretch()
        self.ui_layout.addLayout(self.layout_ad_search)
        
        ## File list
        self.ui_filelist = QTreeWidget()
        self.ui_filelist.setColumnCount(2)
        colNames = QStringList()
        colNames.append("MD5 Hash")
        colNames.append("Category")
        colNames.append("S")
        colNames.append("Published")
        colNames.append("Title")
        self.ui_filelist.setHeaderLabels(colNames)
        self.ui_filelist.hideColumn(0) # hide column with hashes
        # set column to min width
        self.ui_filelist.resizeColumnToContents(1)
        self.ui_filelist.resizeColumnToContents(2) 
        self.ui_filelist.resizeColumnToContents(3)
        
        self.ui_filelist.itemPressed.connect(self.selectFile)
        self.ui_filelist.itemDoubleClicked.connect(self.openFileInReader)
        
        #create contex menu
        self.ui_filelist.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.ui_filelist.addAction(openFileAction)
        self.ui_filelist.addAction(editFileAction)
        self.ui_filelist.addAction(removeFileAction)
        self.ui_filelist.addAction(updateFileAction_Link)
        self.ui_filelist.addAction(updateFileAction_EH)
        
        self.ui_layout.addWidget(self.ui_filelist, 1)
        
        ## File details 
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

    def updateInfoFromLink(self):
        """
        Updates files info with information from URL link.
        """
        if self.selectedFile is None:
            logger.debug('No file selected, nothing to update.')
            QMessageBox.information(self, 'Message', 'No file selected, nothing to update.')
        else:
            url = QInputDialog.getText(self, 'Update file info from url', 'Enter ehentai.org gallery link:')
            if url[1] == True:
                self.manager.updateFileInfoEHentai(self.selectedFile, str(url[0]))
                self.search()
                
    def updateInfoFromEH(self):
        if self.selectedFile is None:
            logger.debug('No file selected, nothing to update.')
            QMessageBox.information(self, 'Message', 'No file selected, nothing to update.')
        else:
            QMessageBox.information(self, 'Message', 'Will now try to search g.e-hentai.org by SHA-1 hash of image in selected file. Will try to search by filename if that fails.')
            gallerylist = self.manager.findFileOnEH(self.selectedFile)
            fileinfo = self.manager.getFileByHash(self.selectedFile)[0]
            app = EHUpdateDialog(fileinfo, gallerylist, parent=self)
            app.exec_()
            returned = app.getClicked()
            if returned is not None:
                eh_gallery = returned[3]
                self.manager.updateFileInfoEHentai(self.selectedFile, str(eh_gallery))
                self.search()
                
    def updateNewFilesFromEH(self):
        QMessageBox.information(self, 'Message', 'Will try to update all new files in database with information from EH.')
        
        newfiles = self.manager.search('', {'new':True})
        
        for n in newfiles:
            gallerylist = self.manager.findFileOnEH(n['hash'])
            app = EHUpdateDialog(n, gallerylist, parent=self)
            app.exec_()
            returned = app.getClicked()
            if returned is not None:
                eh_gallery = returned[3]
                self.manager.updateFileInfoEHentai(n['hash'], str(eh_gallery))
        
        QMessageBox.information(self, 'Message', 'Updates finished')
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
        
    def openFileInReader(self):
        """
        When user double clicks on item in list run external manga viewer (default is mcomix).
        """
        logger.debug('Opening file in external reader.')
        if self.selectedFile is None:
            logger.debug('No file selected, nothing to open.')
            QMessageBox.information(self, 'Message', 'No file selected, nothing to open.')
        else:
            filehash = str(self.selectedFile)
            filepath_rel = self.manager.getFileByHash(filehash)[0]['filepath']
            filepath = os.path.join(self.gallerypath, filepath_rel)
            
            # get path to executable of external archive reader
            reader = self.manager.getSettings()['reader']
            
            systemCommand = reader+' "'+filepath.encode('utf-8')+'"'
            logger.debug('Running: '+systemCommand)
            thread.start_new_thread(os.system, (systemCommand,))
        
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
            app = EditDetails(self.manager, str(self.selectedFile), parent=self)
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
        app = EditSettings(self.manager, parent=self)
        app.exec_()
            
    def search(self):
        """
        Displays filtered data from database
        """
        searchstring = str(self.ui_searchbar.text())
        logger.debug('Searching -> '+str(searchstring))
        
        search_categories = [] 
        for c_btn in self.ui_btn_categories:
            if c_btn.isChecked():
                search_categories.append(unicode(c_btn.text()))
        
        sort = unicode(self.ui_combobox_sort.itemText(self.ui_combobox_sort.currentIndex())).encode('utf-8')
        
        self.search_cfg = {
            'new': (self.ui_box_new.checkState()==QtCore.Qt.Checked),
            'del': (self.ui_box_del.checkState()==QtCore.Qt.Checked),
            'categories': search_categories,
            'sort': sort,
            'sort_rev': (self.ui_box_sort_rev.checkState()==QtCore.Qt.Checked)
            }
        
        filteredlist = self.manager.search(searchstring, self.search_cfg)
        
        self.ui_filelist.clear()
        for f in filteredlist:
            treeItem = QTreeWidgetItem(self.ui_filelist)
            treeItem.setText(0, f['hash'])
            treeItem.setText(1, f['category'])
            
            status = ''
            if f['new']:
                status += 'N'
            if not os.path.isfile(os.path.join(self.gallerypath, f['filepath'])):
                status += 'D'
            treeItem.setText(2, status)
            
            published_date = datetime.datetime.fromtimestamp(f['published']).strftime('%Y-%m-%d %H:%M:%S')
            treeItem.setText(3, published_date)
            
            if f['title']!='':
                title = f['title']
            else:
                title = f['title_jpn']
            treeItem.setText(4, title)
        
        # set min size of columns
        self.ui_filelist.resizeColumnToContents(1)
        self.ui_filelist.resizeColumnToContents(2) 
        self.ui_filelist.resizeColumnToContents(3) 
        
        self.selectedFile = None
        self.showFileDetails()
        
    def clearSearch(self):
        """
        Displays list of all files in database
        """
        self.ui_searchbar.setText('')
        self.search()
        
class ShowDetails(QDialog):
    def __init__(self, manager, filehash=None, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.manager = manager
        self.filehash = filehash
        
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
        layout_main = QHBoxLayout()
        layout_main.setSpacing(5)
        
        # add thumbnail
        thumb_path = os.path.join(self.manager.thumbpath, self.fileinfo['hash']+'.png')
        if not os.path.isfile(thumb_path):
            thumb_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../res/nothumb.png')

        self.ui_thumb = QLabel()
        myPixmap = QtGui.QPixmap(thumb_path)
        #myScaledPixmap = myPixmap.scaled(self.ui_thumb.size(), Qt.KeepAspectRatio)
        self.ui_thumb.setPixmap(myPixmap)
        
        layout_main.addWidget(self.ui_thumb)
        
        ## Basic info
        layout_info = QVBoxLayout()
        layout_info.setSpacing(2)
        
        if self.fileinfo['title']!='':
            self.ui_title = QLabel('<b>Title:</b>  '+self.fileinfo['title'])
            self.ui_title.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            self.ui_title.setWordWrap(True)
            layout_info.addWidget(self.ui_title)
            
        if self.fileinfo['title_jpn']!='':
            self.ui_title_jpn = QLabel('<b>Title [Jpn]:</b>  '+self.fileinfo['title_jpn'])
            self.ui_title_jpn.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            self.ui_title_jpn.setWordWrap(True)
            layout_info.addWidget(self.ui_title_jpn)
            
        self.ui_category = QLabel('<b>Category:</b>  '+self.fileinfo['category'])
        self.ui_category.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_category.setWordWrap(True)
        layout_info.addWidget(self.ui_category)
        
        self.ui_description = QLabel('<b>Description:</b>  '+self.fileinfo['description'])
        self.ui_description.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_description.setWordWrap(True)
        layout_info.addWidget(self.ui_description)
        
        ## Tags
        hr1 = QFrame()
        hr1.setFrameShape(QFrame.HLine)
        layout_info.addWidget(hr1)
        
        # get list of main namespaces from config
        namespaces = self.manager.getSettings()['namespaces']
        
        # standard tag namespaces
        for tc in namespaces:
            if tc in self.fileinfo['tags']:
                tags = QLabel('<b>'+tc+':</b> '+', '.join(self.fileinfo['tags'][tc]))
                tags.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                tags.setWordWrap(True)
                layout_info.addWidget(tags)
        
        # other non-standard tag namespaces
        for tc in self.fileinfo['tags']:
            if not (tc in namespaces):
                tags = QLabel('<b>'+tc+':</b> '+', '.join(self.fileinfo['tags'][tc]))
                tags.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                tags.setWordWrap(True)
                layout_info.addWidget(tags)
        
        # no tags
        if len(self.fileinfo['tags']) == 0:
            notags = QLabel('No tags')    
            notags.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            notags.setWordWrap(True)
            layout_info.addWidget(notags)    
            
        ## Database info
        hr2 = QFrame()
        hr2.setFrameShape(QFrame.HLine)
        layout_info.addWidget(hr2)
        
        # Filepath
        self.ui_filepath = QLabel('<b>Filepath:</b>  $GALLERY/'+self.fileinfo['filepath'])
        self.ui_filepath.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_filepath.setWordWrap(True)
        layout_info.addWidget(self.ui_filepath)
        
        # published
        published_date = datetime.datetime.fromtimestamp(self.fileinfo['published']).strftime('%Y-%m-%d %H:%M:%S')
        self.ui_published = QLabel('<b>Published:</b>  '+published_date)
        self.ui_published.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_published.setWordWrap(True)
        layout_info.addWidget(self.ui_published) 
        
        # new file
        self.ui_new = QLabel('<b>Newfile:</b>  '+str(self.fileinfo['new']))
        self.ui_new.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_new.setWordWrap(True)
        layout_info.addWidget(self.ui_new) 
        
        ## add stretch
        layout_info.addStretch()
        
        ## Setup layout
        layout_main.addLayout(layout_info, 1)
        self.setLayout(layout_main)
        self.show()
        
    def initUI_E(self):
        layout_main = QVBoxLayout()
        self.setLayout(layout_main)
        self.show()
        
class EditDetails(QDialog):
    def __init__(self, manager, filehash, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.manager = manager
        self.filehash = filehash
        self.old_fileinfo = self.manager.getFileByHash(self.filehash)[0]
        self.new_fileinfo = {}

        self.initUI()
        
        if self.old_fileinfo['new']:
            self.new_box.setCheckState(Qt.Checked)
        else:
            self.new_box.setCheckState(Qt.Unchecked)
        
        self.resize(700, 50)
        
    def initUI(self):
        self.setWindowTitle('Edit fileinfo')
        
        layout_main = QGridLayout()
        layout_main.setSpacing(5)
        rstart = 0
        
        # Fileinfo form - titles
        self.line_title = QLineEdit(self.old_fileinfo['title'])
        self.line_title_jpn = QLineEdit(self.old_fileinfo['title_jpn'])
        
        layout_main.addWidget(QLabel('<b>Title:</b> '), rstart + 0, 0)
        layout_main.addWidget(self.line_title, rstart + 0, 1)
        layout_main.addWidget(QLabel('<b>Title [Jpn]:</b> '), rstart + 1, 0)
        layout_main.addWidget(self.line_title_jpn, rstart + 1, 1)
        rstart+=2
        
        # Fileinfo form - category
        categories = self.manager.getSettings()['categories']
        
        self.combobox_category = QComboBox()
        self.combobox_category.addItems(categories)
        if not self.old_fileinfo['category'] in categories:
            self.combobox_category.addItem(self.old_fileinfo['category'])
            
        selectedIndex = self.combobox_category.findText(self.old_fileinfo['category'])
        self.combobox_category.setCurrentIndex(selectedIndex)
        
        layout_main.addWidget(QLabel('<b>Category:</b> '), rstart + 0, 0)
        layout_main.addWidget(self.combobox_category, rstart + 0, 1)
        rstart+=1
        
        # Fileinfo form - description
        self.line_description = QTextEdit(self.old_fileinfo['description'])
        
        layout_main.addWidget(QLabel('<b>Description:</b> '), rstart + 0, 0)
        layout_main.addWidget(self.line_description, rstart + 0, 1)
        rstart+=1
        
        # Fileinfo form - published
        self.line_published = QLineEdit(str(self.old_fileinfo['published']))
        
        layout_main.addWidget(QLabel('<b>Published (UNIX ts):</b> '), rstart + 0, 0)
        layout_main.addWidget(self.line_published, rstart + 0, 1)
        rstart+=1
        
        # Fileinfo form - newfile
        self.new_box = QCheckBox('New file', self)
        
        layout_main.addWidget(self.new_box, rstart + 0, 0, 1, 2)
        rstart+=1
        
        ## Fileinfo form - tags
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
        
        self.new_fileinfo['title'] = unicode(self.line_title.text()).encode('utf-8')
        self.new_fileinfo['title_jpn'] = unicode(self.line_title_jpn.text()).encode('utf-8')
        self.new_fileinfo['category'] = unicode(self.combobox_category.itemText(self.combobox_category.currentIndex())).encode('utf-8')
        self.new_fileinfo['description'] = unicode(self.line_description.toPlainText()).encode('utf-8')
        self.new_fileinfo['published'] = int(self.line_published.text())
        self.new_fileinfo['new'] = (self.new_box.checkState()==QtCore.Qt.Checked)
        
        self.new_fileinfo['tags'] = {}
        for tc in self.line_tags:
            if str(self.line_tags[tc].text()).strip() != '':
                t_list = [t.strip() for t in unicode(self.line_tags[tc].text()).encode('utf-8').lower().split(',')]
                self.new_fileinfo['tags'][tc] = t_list
        
        self.manager.updateFileInfo(self.filehash, self.new_fileinfo)
        self.close()
        
class EditSettings(QDialog):
    def __init__(self, manager, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.manager = manager
        self.old_settings = self.manager.getSettings()
        self.new_settings = {}

        self.initUI()
        
        self.resize(700, 50)
        
    def initUI(self):
        self.setWindowTitle('Edit settings')
        
        layout_main = QGridLayout()
        layout_main.setSpacing(5)
        rstart = 0
        
        ## Fileinfo form - basic
        self.line_reader = QLineEdit(self.old_settings['reader'])
        self.line_allow_ext = QLineEdit(self.old_settings['allowed_extensions'])
        self.line_categories = QLineEdit(', '.join(self.old_settings['categories']))
        self.line_categories_enabled = QLineEdit(', '.join(self.old_settings['categories_enabled']))
        self.line_namespaces = QLineEdit(', '.join(self.old_settings['namespaces']))
        
        layout_main.addWidget(QLabel('<b>Reader:</b> '), rstart + 0, 0)
        layout_main.addWidget(self.line_reader, rstart + 0, 1)
        layout_main.addWidget(QLabel('<b>Allowed extensions:</b> '), rstart + 1, 0)
        layout_main.addWidget(self.line_allow_ext, rstart + 1, 1)
        layout_main.addWidget(QLabel('<b>Categories:</b> '), rstart + 2, 0)
        layout_main.addWidget(self.line_categories, rstart + 2, 1)
        layout_main.addWidget(QLabel('<b>Categories enabled:</b> '), rstart + 3, 0)
        layout_main.addWidget(self.line_categories_enabled, rstart + 3, 1)
        layout_main.addWidget(QLabel('<b>Namespaces:</b> '), rstart + 4, 0)
        layout_main.addWidget(self.line_namespaces, rstart + 4, 1)
        rstart+=5
        
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
        
        self.new_settings['reader'] = unicode(self.line_reader.text()).encode('utf-8')
        
        self.new_settings['allowed_extensions'] = [x.strip() for x in unicode(self.line_allow_ext.text()).encode('utf-8').lower().split(',')]
        
        self.new_settings['categories'] = [x.strip() for x in unicode(self.line_categories.text()).encode('utf-8').lower().split(',')]
        self.new_settings['categories_enabled'] = [x.strip() for x in unicode(self.line_categories_enabled.text()).encode('utf-8').lower().split(',')]
        
        self.new_settings['namespaces'] = [x.strip() for x in unicode(self.line_namespaces.text()).encode('utf-8').lower().split(',')]
        
        self.manager.saveSettings(self.new_settings)
        self.close()
        
        
