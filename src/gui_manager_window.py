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

import os
import thread
import datetime

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gallery_manager import GalleryManager
from gui_eh_update_dialog import EHUpdateDialog
from gui_edit_settings import EditSettings
from gui_edit_details import EditDetails
from gui_find_update_files import FindNewDialog
from gui_find_update_files import UpdateSearchDialog

class ManagerWindow(QMainWindow):
    def __init__(self, gallerypath):
        QMainWindow.__init__(self)
        
        self.gallerypath = unicode(gallerypath)
        self.manager = GalleryManager(self.gallerypath)
        self.selectedFile = None
        self.filteredlist = None
  
        self.resize(1000, 700)
        self.initUI()        
        
        self.ui_searchbar.setText('')
        self.search()
        
        # autologin to eh
        if self.manager.loadSavedCookies():
            eh_li_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../res/eh-state-login.png")
            self.ehMenu.setIcon(QIcon(eh_li_path))
    
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
        
        updateSearchEHAction = QtGui.QAction('Update search from EH', self)
        updateSearchEHAction.setStatusTip('Automatically updates info of searched files with information from EH')
        updateSearchEHAction.triggered.connect(self.updateSearchFromEH)
        
        fixPathsAction = QtGui.QAction('Fix paths', self)
        fixPathsAction.setStatusTip('Fixes paths to files in gallery (run if moved or renamed file)')
        fixPathsAction.triggered.connect(self.manager.fixFilepaths)
        
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
        fileMenu.addAction(fixPathsAction)
        fileMenu.addAction(updateSearchEHAction)
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
        
        ## EH login
        getLoginAction = QtGui.QAction('Check state', self)
        getLoginAction.setStatusTip('Check if you are logged to e-hentai.org')
        getLoginAction.triggered.connect(self.getLogin)
        
        loginAction = QtGui.QAction('Login to EH', self)
        loginAction.setStatusTip('Login to e-hentai.org')
        loginAction.triggered.connect(self.loginToEH)
        
        logoutAction = QtGui.QAction('Logout from EH', self)
        logoutAction.setStatusTip('Logout from e-hentai.org')
        logoutAction.triggered.connect(self.logoutFromEH)
        
        self.ehMenu = menubar.addMenu('EH')
        self.ehMenu.addAction(getLoginAction)
        self.ehMenu.addAction(loginAction)
        self.ehMenu.addAction(logoutAction)
        eh_lo_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../res/eh-state-logout.png")
        self.ehMenu.setIcon(QIcon(eh_lo_path))
        
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
            
        self.ui_btn_category_other = QtGui.QPushButton('OTHER', self)
        self.ui_btn_category_other.setCheckable(True)
        self.ui_btn_category_other.setChecked(True)
        self.layout_cat_search.addWidget(self.ui_btn_category_other)
        
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
        
    def loginToEH(self):
        app = LoginDialog(parent=self)
        app.exec_()
        username, password, save = app.getLoginDetails()
        
        state = self.manager.loginToEH(username,password)
        if state:
            QMessageBox.information(self, 'Message', 'Logged in EH.')
            eh_li_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../res/eh-state-login.png")
            self.ehMenu.setIcon(QIcon(eh_li_path))
            if save:
                self.manager.saveCookies()
        else:
            QMessageBox.warning(self, 'Error', 'Login failed')
            eh_lo_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../res/eh-state-logout.png")
            self.ehMenu.setIcon(QIcon(eh_lo_path))
        
    def logoutFromEH(self):
        self.manager.loginToEH('','')
        QMessageBox.information(self, 'Message', 'Logged out from EH.')
        eh_lo_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../res/eh-state-logout.png")
        self.ehMenu.setIcon(QIcon(eh_lo_path))
        
    def getLogin(self):
        if self.manager.getLogin():
            QMessageBox.information(self, 'Message', 'Logged in')
        else:
            QMessageBox.information(self, 'Message', 'Not logged in')
        
    def showError(self, err):
        """
        Shows message box with error
        """
        if err%10==0:
            return # no error
        elif err==1:
            QMessageBox.warning(self, 'Error', 'Failed: EH Overload')
        elif err==2:
            QMessageBox.warning(self, 'Error', 'Failed: EH Banned')
        elif err==3:
            QMessageBox.warning(self, 'Error', 'Failed: EH undefined error')
        elif err==11:
            QMessageBox.warning(self, 'Error', 'Failed: EH gallery html page is not accesable')
        elif err==21:
            QMessageBox.warning(self, 'Error', 'Failed: EH API error')
        elif err==31:
            QMessageBox.warning(self, 'Error', 'Failed: Image hash couldnt be generated')
        else:
            QMessageBox.warning(self, 'Error', 'Failed: '+str(err))

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
                err = self.manager.updateFileInfoEHentai(self.selectedFile, str(url[0]))
                
                self.showError(err)
                
                if err==0:
                    self.search()
                
    def updateInfoFromEH(self):
        if self.selectedFile is None:
            logger.debug('No file selected, nothing to update.')
            QMessageBox.information(self, 'Message', 'No file selected, nothing to update.')
        else:
            QMessageBox.information(self, 'Message', 'Will now try to search for information on EH with hash of image in selected file.')
            gallerylist, err = self.manager.findFileOnEH(self.selectedFile)
            if err!=0:
                self.showError(err)
                return
            
            fileinfo = self.manager.getFileByHash(self.selectedFile)[0]
            app = EHUpdateDialog(fileinfo, gallerylist, parent=self)
            app.exec_()
            returned = app.getClicked()
            if returned is not None:
                eh_gallery = returned[3]
                err = self.manager.updateFileInfoEHentai(self.selectedFile, str(eh_gallery))
                
                self.showError(err)
                
                if err==0:
                    self.search()
        
    def updateSearchFromEH(self):
        self.statusBar().showMessage('Updating filtered list of files...')
        QtCore.QCoreApplication.processEvents()
        
        app = UpdateSearchDialog(self.manager, self.filteredlist, parent=self)
        app.exec_()
        
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
        self.ui_info.changeDetails(self.selectedFile)
        
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
            
            systemCommand = '"'+reader+'" "'+filepath.encode('utf-8')+'"'
            if os.name == 'nt':
                systemCommand = '"'+systemCommand+'"'
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
            newfilepath = unicode(newfilepath).encode("utf8")
            filehash = self.manager.getHash(newfilepath)
            self.manager.addFile(newfilepath, filehash)
            
            msgBox = QMessageBox()
            msgBox.setText("Do you want update file info from EH?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.Yes)
            ret = msgBox.exec_()
            
            if ret == QMessageBox.Yes:
                gallerylist, err = self.manager.findFileOnEH(filehash)
                if err!=0:
                    self.showError(err)
                    return
                
                fileinfo = self.manager.getFileByHash(filehash)[0]
                app = EHUpdateDialog(fileinfo, gallerylist, parent=self)
                app.exec_()
                returned = app.getClicked()
                if returned is not None:
                    eh_gallery = returned[3]
                    err = self.manager.updateFileInfoEHentai(filehash, str(eh_gallery))
                    
                    self.showError(err)
            
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
        QtCore.QCoreApplication.processEvents()
        
        app = FindNewDialog(self.manager, parent=self)
        app.exec_()
        
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
        
        # other categories button
        categories_other = self.ui_btn_category_other.isChecked()
        
        # main categories buttons
        search_categories = [] 
        for c_btn in self.ui_btn_categories:
            if c_btn.isChecked():
                search_categories.append(unicode(c_btn.text()))
                
        # if no buttons pressed, search all
        if len(search_categories)==0 and not categories_other:
            for c_btn in self.ui_btn_categories:
                search_categories.append(unicode(c_btn.text()))
            categories_other = True
        
        sort = unicode(self.ui_combobox_sort.itemText(self.ui_combobox_sort.currentIndex())).encode('utf-8')
        
        self.search_cfg = {
            'new': (self.ui_box_new.checkState()==QtCore.Qt.Checked),
            'del': (self.ui_box_del.checkState()==QtCore.Qt.Checked),
            'categories': search_categories,
            'categories_other': categories_other,
            'sort': sort,
            'sort_rev': (self.ui_box_sort_rev.checkState()==QtCore.Qt.Checked)
            }
        
        self.filteredlist = self.manager.search(searchstring, self.search_cfg)
        
        self.ui_filelist.clear()
        for f in self.filteredlist:
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
        
        # set minimal height (thumb + border)
        self.setMinimumHeight(self.manager.THUMB_MAXSIZE[1]+15)
        
        self.initUI()
        self.changeDetails(filehash)
        
    def initUI(self):
        layout_main = QHBoxLayout()
        layout_main.setSpacing(5)
        
        # add thumbnail
        thumb_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../res/nothumb.png')
        self.ui_thumb = QLabel()
        myPixmap = QtGui.QPixmap(thumb_path)
        self.ui_thumb.setPixmap(myPixmap)
        
        layout_main.addWidget(self.ui_thumb)
        
        ## Basic info
        layout_info = QVBoxLayout()
        layout_info.setSpacing(2)
        
        self.ui_title = QLabel()
        self.ui_title.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_title.setWordWrap(True)
        layout_info.addWidget(self.ui_title)
            
        self.ui_title_jpn = QLabel()
        self.ui_title_jpn.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_title_jpn.setWordWrap(True)
        layout_info.addWidget(self.ui_title_jpn)
        
        self.ui_category = QLabel()
        self.ui_category.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_category.setWordWrap(True)
        layout_info.addWidget(self.ui_category)
        
        self.ui_description = QLabel()
        self.ui_description.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_description.setWordWrap(True)
        layout_info.addWidget(self.ui_description)
        
        ## Tags
        hr1 = QFrame()
        hr1.setFrameShape(QFrame.HLine)
        layout_info.addWidget(hr1)
        
        self.layout_tags = QVBoxLayout()
        self.layout_tags.setSpacing(2)
        
        layout_info.addLayout(self.layout_tags)
        
        ## Database info
        hr2 = QFrame()
        hr2.setFrameShape(QFrame.HLine)
        layout_info.addWidget(hr2)
        
        # Filepath
        self.ui_filepath = QLabel()
        self.ui_filepath.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_filepath.setWordWrap(True)
        layout_info.addWidget(self.ui_filepath)
        
        # published
        self.ui_published = QLabel()
        self.ui_published.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_published.setWordWrap(True)
        layout_info.addWidget(self.ui_published) 
        
        # new file
        self.ui_new = QLabel()
        self.ui_new.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.ui_new.setWordWrap(True)
        layout_info.addWidget(self.ui_new) 
        
        ## add stretch
        layout_info.addStretch()
        
        ## Setup layout
        layout_main.addLayout(layout_info, 1)
        self.setLayout(layout_main)
        self.show()
        
    def changeDetails(self, filehash):
        self.filehash = filehash
        
        # remove old tags in layout
        for i in reversed(range(self.layout_tags.count())):
            widget = self.layout_tags.takeAt(i).widget()

            if widget is not None: 
                # widget will be None if the item is a layout
                widget.deleteLater()
        
        if self.filehash is None or str(self.filehash)=='':
            logger.debug('No file selected, nothing to display.')
            self.fileinfo = None
            
            # thumb
            thumb_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../res/nothumb.png')
            myPixmap = QtGui.QPixmap(thumb_path)
            self.ui_thumb.setPixmap(myPixmap)
            
            # basic info
            self.ui_title.setText('<b>Title:</b>')
            self.ui_title_jpn.setText('<b>Title [Jpn]:</b>')
            self.ui_category.setText('<b>Category:</b>')
            self.ui_description.setText('<b>Description:</b>')
            
            # tags
            notags = QLabel('No tags')    
            notags.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            notags.setWordWrap(True)
            self.layout_tags.addWidget(notags) 
            
            ## Database info
            self.ui_filepath.setText('<b>Filepath:</b>')
            self.ui_published.setText('<b>Published:</b>')
            self.ui_new.setText('<b>Newfile:</b>')
            
        else:
            logger.debug('Display info for -> '+self.filehash)
            self.fileinfo = self.manager.getFileByHash(self.filehash)[0]
            logger.debug(str(self.fileinfo))
            
            # thumb
            thumb_path = os.path.join(self.manager.thumbpath, self.fileinfo['hash']+'.png')
            if not os.path.isfile(thumb_path):
                thumb_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../res/nothumb.png')
            myPixmap = QtGui.QPixmap(thumb_path)
            self.ui_thumb.setPixmap(myPixmap)
            
            # basic info
            self.ui_title.setText('<b>Title:</b>  '+self.fileinfo['title']) 
            self.ui_title_jpn.setText('<b>Title [Jpn]:</b>  '+self.fileinfo['title_jpn'])
            self.ui_category.setText('<b>Category:</b>  '+self.fileinfo['category'])
            self.ui_description.setText('<b>Description:</b>  '+self.fileinfo['description'])
            
            ## tags
            # get list of main namespaces from config
            namespaces = self.manager.getSettings()['namespaces']
            
            # standard tag namespaces
            for tc in namespaces:
                if tc in self.fileinfo['tags']:
                    tags = QLabel('<b>'+tc+':</b> '+', '.join(self.fileinfo['tags'][tc]))
                    tags.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                    tags.setWordWrap(True)
                    self.layout_tags.addWidget(tags)
            
            # other non-standard tag namespaces
            for tc in self.fileinfo['tags']:
                if not (tc in namespaces):
                    tags = QLabel('<b>'+tc+':</b> '+', '.join(self.fileinfo['tags'][tc]))
                    tags.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                    tags.setWordWrap(True)
                    self.layout_tags.addWidget(tags)
            
            # no tags
            if len(self.fileinfo['tags']) == 0:
                notags = QLabel('No tags')    
                notags.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                notags.setWordWrap(True)
                self.layout_tags.addWidget(notags)  
            
            ## Database info
            self.ui_filepath.setText('<b>Filepath:</b>  $GALLERY/'+self.fileinfo['filepath'])
            published_date = datetime.datetime.fromtimestamp(self.fileinfo['published']).strftime('%Y-%m-%d %H:%M:%S')
            self.ui_published.setText('<b>Published:</b>  '+published_date)
            self.ui_new.setText('<b>Newfile:</b>  '+str(self.fileinfo['new']))

            
        
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.initUI()
    
    def initUI(self):
        layout_main = QVBoxLayout()
        layout_main.setSpacing(5)
        
        self.setWindowTitle('Login')
        
        ## add edits + button
        self.line_username = QLineEdit()
        self.line_password = QLineEdit()
        self.line_password.setEchoMode(QLineEdit.Password)
        
        layout_main.addWidget(QLabel('Username:'))
        layout_main.addWidget(self.line_username)
        layout_main.addWidget(QLabel('Password:'))
        layout_main.addWidget(self.line_password) 
        
        # Fileinfo form - newfile
        self.box_save = QCheckBox('Save cookies for autologin', self)
        layout_main.addWidget(self.box_save)
        
        # login button
        self.btn_login = QPushButton('Login')
        self.btn_login.pressed.connect(self.accept)
        layout_main.addWidget(self.btn_login)
        
        ## add stretch
        layout_main.addStretch()
        
        ## Setup layout
        self.setLayout(layout_main)
        self.show()
        
    def getLoginDetails(self):
        return unicode(self.line_username.text()), unicode(self.line_password.text()), (self.box_save.checkState()==QtCore.Qt.Checked)
