Install
======

Linux (Debian/Ubuntu/Mint)
-------
Get zipped source and extract it anywhere you want:

    https://github.com/kunesj/EH-file-manager

Run this to install required dependencies:

    sudo apt-get install python python-pip python-sqlite python-qt4 python-imaging python-yaml python-dateutil unrar python-lzma python-beautifulsoup python-requests
    wget http://ftp.us.debian.org/debian/pool/main/p/python-rarfile/python-rarfile_2.6-1_all.deb -O python-rarfile.deb
    sudo dpkg -i python-rarfile.deb
    sudo apt-get -f install
    
(Optional) Install mcomix:

    sudo apt-get install mcomix

Windows
-------
!!Warning!! Main development is on Linux, so Windows version may be very buggy.

Get zipped source and extract it anywhere you want:

    https://github.com/kunesj/EH-file-manager
    
Install Python 2, setupTools, pip, PyQt4 and pylzma:

- [Python 2.x](https://www.python.org/downloads/windows/)
- [Python 2.x - setupTools](http://www.lfd.uci.edu/~gohlke/pythonlibs/#setuptools)
- [Python 2.x - pip](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip)
- [Python 2.x - PyQt4](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt)
- [Python 2.x - pylzma](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pylzma)

Run this to install rest of required dependencies:

    C:\Python27\Scripts\pip.exe install requests beautifulsoup4 rarfile pillow pyyaml python-dateutil 

Download [unrar](http://www.rarlab.com/rar/unrarw32.exe) and install it to Python directory, result should look like this:

    C:\Python27\unrar.exe

(Optional) Install [mcomix](http://sourceforge.net/projects/mcomix/files/)

- In EH File Manager settings add full path to mcomix executable
