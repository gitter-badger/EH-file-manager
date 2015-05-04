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

class EHUpdateDialog(QDialog):
    def __init__(self, fileinfo, gallery_list = [], parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.old_fileinfo = fileinfo
        self.gallery_list = gallery_list
        self.initUI()
        
        self.resize(700, 50)
        
    def initUI(self):
        self.setWindowTitle('Update from EH')
        
        layout_main = QVBoxLayout()
        layout_main.setSpacing(5)
        
        # Title
        title = QLabel('Select e-hentai.org gallery to load file information from')
        font_label = QFont()
        font_label.setBold(True)   
        font_label.setPixelSize(20)
        title.setFont(font_label)
        title.setAlignment(Qt.AlignCenter)
        
        layout_main.addWidget(title)
        
        # Info
        label_orig_info = QLabel('<b>Searched file information</b>')
        font_orig_info = QFont()
        font_orig_info.setPixelSize(15)
        label_orig_info.setFont(font_orig_info)
        label_fp = QLabel('<b>Filepath:</b> $GALLERY/'+self.old_fileinfo['filepath'])
        label_fp.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        label_ft = QLabel('<b>Title:</b> '+self.old_fileinfo['title'])
        label_ft.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        label_ftj = QLabel('<b>Title [Jpn]:</b> '+self.old_fileinfo['title_jpn'])
        label_ftj.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        layout_main.addWidget(label_orig_info)
        layout_main.addWidget(label_fp)
        layout_main.addWidget(label_ft)
        layout_main.addWidget(label_ftj)
        
        ## Add radio buttons
        self.radio = []
        
        # this is added after everything else
        none_radio = QRadioButton("Don't change anything")
        self.radio.append(none_radio)
        
        layout_radio = QGridLayout()
        layout_radio.setSpacing(5)
        layout_radio.setColumnStretch(3, 1)
        rstart = 0
        
        # categories
        hr1 = QFrame()
        hr1.setFrameShape(QFrame.HLine)
        layout_radio.addWidget(hr1, rstart + 0, 0, 1, 5)
        rstart+=1
        
        layout_radio.addWidget(QLabel(), rstart, 0)
        layout_radio.addWidget(QLabel('| <b>Category</b>'), rstart, 1) 
        layout_radio.addWidget(QLabel('| <b>Published</b>'), rstart, 2) 
        layout_radio.addWidget(QLabel('| <b>Title</b>'), rstart, 3) 
        layout_radio.addWidget(QLabel('| <b>Uploader</b>'), rstart, 4) 
        rstart+=1
        
        hr2 = QFrame()
        hr2.setFrameShape(QFrame.HLine)
        layout_radio.addWidget(hr2, rstart + 0, 0, 1, 5)
        rstart+=1
        
        for g in self.gallery_list:
            new_radio = QRadioButton()
            self.radio.append(new_radio)
            layout_radio.addWidget(new_radio, rstart, 0)
            layout_radio.addWidget(QLabel(u'| '+g[0]), rstart, 1) # category
            layout_radio.addWidget(QLabel(u'| '+g[1]), rstart, 2) # time
            new_title = QLabel(u'| '+g[2])
            new_title.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            layout_radio.addWidget(new_title, rstart, 3) # title
            layout_radio.addWidget(QLabel(u'| '+g[4]), rstart, 4) # uploader
            rstart+=1
        
        if len(self.gallery_list) == 0:
            label_nothingfound = QLabel('No similar galleries found')
            label_nothingfound.setAlignment(Qt.AlignCenter)
            layout_radio.addWidget(label_nothingfound, rstart, 0, 1, 5)
            rstart+=1
            
        if len(self.radio)==1:
            self.radio[0].setChecked(True)
        else:
            self.radio[1].setChecked(True)
            
        hr3 = QFrame()
        hr3.setFrameShape(QFrame.HLine)
        layout_radio.addWidget(hr3, rstart + 0, 0, 1, 5)
        rstart+=1
        
        layout_main.addLayout(layout_radio)
        
        layout_main.addWidget(none_radio)
        
        ## Close Button
        btn_accept = QPushButton('Accept')
        btn_accept.pressed.connect(self.accept)
        layout_main.addWidget(btn_accept)
        
        ## Stretcher
        layout_main.addStretch()
        
        ## Setup layout
        self.setLayout(layout_main)
        self.show()
        
    def getClicked(self):
        for i in range(0, len(self.radio)):
            if self.radio[i].isChecked():
                if i == 0:
                    return None
                else:
                    return self.gallery_list[i-1]
                
        return None
        
