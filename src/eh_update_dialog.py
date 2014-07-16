# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class EHUpdateDialog(QDialog):
    def __init__(self, manager, gallery_list = [], parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.manager = manager
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
        
        ## Add radio buttons
        self.radio = []
        
        # this is added after everything else
        none_radio = QRadioButton('< Dont change anything >')
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
            layout_radio.addWidget(QLabel(u'| '+g[2]), rstart, 3) # title
            layout_radio.addWidget(QLabel(u'| '+g[4]), rstart, 4) # uploader
            rstart+=1
        
        if len(self.gallery_list) == 0:
            label_nothingfound = QLabel('No similar galleries found')
            label_nothingfound.setAlignment(Qt.AlignCenter)
            layout_radio.addWidget(label_nothingfound, rstart, 0, 1, 5)
            rstart+=1
            
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
        
