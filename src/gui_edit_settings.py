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
        self.line_allow_ext = QLineEdit(', '.join(self.old_settings['allowed_extensions']))
        self.line_delay = QLineEdit(str(self.old_settings['eh_delay']))
        self.line_overload_delay = QLineEdit(str(self.old_settings['eh_overload_delay']))
        self.line_categories = QLineEdit(', '.join(self.old_settings['categories']))
        self.line_categories_enabled = QLineEdit(', '.join(self.old_settings['categories_enabled']))
        self.line_namespaces = QLineEdit(', '.join(self.old_settings['namespaces']))
        
        layout_main.addWidget(QLabel('<b>Reader:</b> '), rstart + 0, 0)
        layout_main.addWidget(self.line_reader, rstart + 0, 1)
        layout_main.addWidget(QLabel('<b>Allowed extensions:</b> '), rstart + 1, 0)
        layout_main.addWidget(self.line_allow_ext, rstart + 1, 1)
        layout_main.addWidget(QLabel('<b>EH delay:</b> '), rstart + 2, 0)
        layout_main.addWidget(self.line_delay, rstart + 2, 1)
        layout_main.addWidget(QLabel('<b>EH overload delay:</b> '), rstart + 3, 0)
        layout_main.addWidget(self.line_overload_delay, rstart + 3, 1)
        layout_main.addWidget(QLabel('<b>Categories:</b> '), rstart + 4, 0)
        layout_main.addWidget(self.line_categories, rstart + 4, 1)
        layout_main.addWidget(QLabel('<b>Categories enabled:</b> '), rstart + 5, 0)
        layout_main.addWidget(self.line_categories_enabled, rstart + 5, 1)
        layout_main.addWidget(QLabel('<b>Namespaces:</b> '), rstart + 6, 0)
        layout_main.addWidget(self.line_namespaces, rstart + 6, 1)
        rstart+=7
        
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
        
        try:
            self.new_settings['eh_delay'] = int(self.line_delay.text())
        except:
            logger.error('Couldnt use settings for eh_delay given by user -> using defaults')
            self.new_settings['eh_delay'] = self.manager.getDefaultSettings()['eh_delay']
            
        try:
            self.new_settings['eh_overload_delay'] = int(self.line_overload_delay.text())
        except:
            logger.error('Couldnt use settings for eh_overload_delay given by user -> using defaults')
            self.new_settings['eh_overload_delay'] = self.manager.getDefaultSettings()['eh_overload_delay']
        
        self.new_settings['categories'] = [x.strip() for x in unicode(self.line_categories.text()).encode('utf-8').lower().split(',')]
        self.new_settings['categories_enabled'] = [x.strip() for x in unicode(self.line_categories_enabled.text()).encode('utf-8').lower().split(',')]
        
        self.new_settings['namespaces'] = [x.strip() for x in unicode(self.line_namespaces.text()).encode('utf-8').lower().split(',')]
        
        self.manager.saveSettings(self.new_settings)
        self.close()
        
      
