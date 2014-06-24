# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

import argparse
import sys
import os

from PyQt4.QtGui import QApplication, QMessageBox, QFileDialog

from gallery_window import GalleryWindow
from gallery_manager import GalleryManager
    
def main():
    # Parasing input prarmeters
    parser = argparse.ArgumentParser(
        description='Man2 (Manga Manager)'
    )
    parser.add_argument(
        '-g', '--gallery',
        default=None,
        help='Path to directory with manga gellery')
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Debug mode')
    args = parser.parse_args()
    
    # Logger configuration
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
        
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
    gw = GalleryWindow(gallerypath)
    sys.exit(app.exec_())
    
        
if __name__ == "__main__":
    main()
