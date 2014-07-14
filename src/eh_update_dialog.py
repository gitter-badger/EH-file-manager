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
        
    def initUI(self):
        self.setWindowTitle('Update from EH')
        
        layout_main = QGridLayout()
        layout_main.setSpacing(5)
        rstart = 0
        
        self.radio = []
        for g in self.gallery_list:
            new_radio = QRadioButton(str(g[2]))
            self.radio.append(new_radio)
            layout_main.addWidget(new_radio, rstart, 0)
            rstart+=1
        
        ## Close Button
        btn_accept = QPushButton('Accept')
        btn_accept.pressed.connect(self.accept)
        layout_main.addWidget(btn_accept, rstart + 0, 0)
        rstart+=1
        
        ## Stretcher
        layout_main.addItem(QSpacerItem(0,0), rstart + 0, 0)
        layout_main.setRowStretch(rstart + 0, 1)
        rstart+=1
        
        ## Setup layout
        self.setLayout(layout_main)
        self.show()
        
    def getClicked(self):
        for i in range(0, len(self.radio)):
            if self.radio[i].isChecked():
                return self.gallery_list[i]
                
        return None
        
