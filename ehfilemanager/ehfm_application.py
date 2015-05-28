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
logging.basicConfig()
logger = logging.getLogger(__name__)

import argparse
import sys
import os

from PyQt4.QtGui import QApplication, QMessageBox, QFileDialog

from gui_manager_window import ManagerWindow
from gallery_manager import GalleryManager
    
def main():
    # Parasing input prarmeters
    parser = argparse.ArgumentParser(
        description='EH file manager'
    )
    parser.add_argument(
        '-g', '--gallery',
        default=None,
        help='Path to directory with archive files')
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Debug mode')
    parser.add_argument(
        '--logfile',
        action='store_true',
        help='Save log to file')
    args = parser.parse_args()
    
    # Logger configuration
    logging.basicConfig(stream=sys.stdout)
    logger = logging.getLogger()
    
    logger.setLevel(logging.WARNING)
    if args.debug:
        logger.setLevel(logging.DEBUG)   
    
    if args.logfile:
        try:
            os.remove("eh_file_manager.log")
        except OSError:
            pass
        fh = logging.FileHandler("eh_file_manager.log")
        fh.setFormatter(logging.Formatter(fmt='%(levelname)s:%(name)s:%(message)s'))
        logger.addHandler(fh)
            
    app = QApplication(sys.argv)
    
    gallerypath = args.gallery
    gm = GalleryManager()
    if gallerypath is not None:
        if not gm.isGallery(gallerypath):
            logger.debug('Bad gallery path!!!')
            msgBox = QMessageBox(QMessageBox.Warning, 'Message', 'Bad gallery path!!!')
            msgBox.exec_()
            gallerypath = None
    
    while gallerypath is None:
        msgBox = QMessageBox()
        msgBox.setText("Do you want to open existing gallery?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Close)
        msgBox.setDefaultButton(QMessageBox.Open)
        ret = msgBox.exec_()
        
        if ret == QMessageBox.Close:
            logger.debug('Exiting')
            sys.exit(0)
        
        new_gallerypath = QFileDialog.getExistingDirectory(
                    caption='Select Gallery Directory',
                    directory='./'
                )
        
        if str(new_gallerypath) == '':
            continue
        elif ret == QMessageBox.No:
            gallerypath = new_gallerypath
        else:
            if not gm.isGallery(new_gallerypath):
                logger.debug('Bad gallery path!!!')
                msgBox = QMessageBox(QMessageBox.Warning, 'Message', 'Bad gallery path!!!')
                msgBox.exec_()
            else:
                gallerypath = new_gallerypath
    app.exit()
    
    # Run main app
    mw = ManagerWindow(gallerypath)
    sys.exit(app.exec_())
    
        
if __name__ == "__main__":
    main()
