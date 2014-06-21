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
        '--nogui',
        action='store_true',
        help='Disable GUI')
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
        
    if args.nogui:
        logger.debug('Running without gui.')
        gallery = GalleryManager()
        gallery.open_path(args.gallery)
        
        filefolder = os.path.join(args.gallery, 'Files')
        c = -1
        while c is not 0:
            c = int(raw_input("1 - to add file\n2 - to get info about file\n0 - to exit\n"))
            if c is 1:
                name = raw_input("Write name of file to add:\n")
                gallery.process_file(os.path.join(filefolder, name))
            elif c is 2:
                name = raw_input("Write name of file:\n")
                print gallery.get_file_info(os.path.join(filefolder, name))
                
        #print gallery.info_from_ehentai_link('http://g.e-hentai.org/g/618395/0439fa3666/')
    else:
        logger.debug('Running with gui.')
        app = QApplication(sys.argv)
        gw = GalleryWindow(args.gallery)
        sys.exit(app.exec_())
        
if __name__ == "__main__":
    main()
