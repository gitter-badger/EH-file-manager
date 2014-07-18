# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

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
        
      
