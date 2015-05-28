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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

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
        
  
