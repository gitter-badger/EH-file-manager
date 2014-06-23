# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

import argparse
import sys
import os

from PyQt4.QtGui import QApplication

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
    
    # Run main app
    app = QApplication(sys.argv)
    gw = GalleryWindow(args.gallery)
    sys.exit(app.exec_())
    
        
if __name__ == "__main__":
    main()
