Install
======

Install on Linux (Debian/Ubuntu/Mint)
-------
There are 3 ways you can do this.

1. Static binary way (Doesnt need root or any installed dependencies)
    - Download archived binary file from latest [release](https://github.com/kunesj/EH-file-manager/releases).
    - Extract "ehfilemanager" file to any folder in your system path (best places are ~/bin or /usr/local/bin).
    - Extract omad.desktop to ~/.local/share/application or /usr/local/share/applications
    - You can now start EH-file-manager with shortcut from global menu or from commandline with "ehfilemanager" command

2. Package install way (Proper Python way)
    - Download archived source from latest [release](https://github.com/kunesj/EH-file-manager/releases).
    - Extract it anywhere you want
    - In terminal in folder with extracted files, run: "make install"
    - Remove folder with extracted source
    - You can now start EH-file-manager with shortcut from global menu or from commandline with "ehfilemanager" command

3. Source only way (For developers)
    - Download archived source from latest [release](https://github.com/kunesj/EH-file-manager/releases).
    - Extract it anywhere you want
    - In terminal in folder with extracted files, run: "make install_dep" to install runtime dependencies
    - You can only start EH-file-manager from commandline, by directly using Python interpreter (python -m ehfilemanager)

Install on Windows
-------  
!!Warning!! Main development is on Linux, so Windows version may be very buggy.

You can download archived binary file from latest [release](https://github.com/kunesj/EH-file-manager/releases) and just use that, or you can follow these instructions and install everything manualy. (When binary for some reason doesnt work)

1. Install Python 2
    - Download [Python 2.x](https://www.python.org/downloads/windows/) installer (includes pip and setuptools)
    - Run installer and select to add python to system path

2. Install PyQt4
    - Download [Python 2.x - PyQt4](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4) wheels package
    - From commandline in folder with downloaded file run following command, you may need to modify it for correct filename: 

    pip install PyQt4-4.11.3-cp27-none-win32.whl
    
3. Install Pylzma
    - Download [Python 2.x - pylzma](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pylzma) wheels package and install it in the same way as before

4. Install unrar
    - Download [unrar](http://www.rarlab.com/rar/unrarw32.exe) and install it somewhere in your system path, for example:

    C:\Python27\unrar.exe

5. Install rest of runtime dependencies
    - From commandline run following command:

    pip install requests beautifulsoup4 rarfile pillow pyyaml python-dateutil 
    
6. Install EH-file-manager
    - Get zipped [source](https://github.com/kunesj/EH-file-manager/releases) and extract it anywhere you want
    - Run following commands from folder with extracted files, to finish installation:
    
    python setup.py build

    python setup.py install

    - You can now start EH-file-manager from commandline with "ehfilemanager" command, optionally you can also create shortcut with this command

7. Install mcomix (optional)
    - Download and install [mcomix](http://sourceforge.net/projects/mcomix/files/)
    - Later start EH File Manager and in settings add full path to mcomix executable

Building static binary
------- 

1. Linux
    - In terminal in omad folder, run: "make build_dep" to install build dependencies
    - Then run: "make build" to build binary and package it together with source into tar archive
    
2. Windows
    - Follow installation instructions, until you install all dependencies
    - Download and install [pywin32](http://sourceforge.net/projects/pywin32) (make sure it's Python 2 version)
    - Download and install [MSVCR](https://www.microsoft.com/en-us/download/details.aspx?id=29)
    - Download and install [Git](https://git-scm.com/downloads), in installation select to use git from windows commandline
    - Download source of development version of [PyInstaller](https://github.com/pyinstaller/pyinstaller)
    - In folder with downloaded PyInstaller files run following commands:

    python setup.py build

    python setup.py install

    - Now go to folder with EH-file-manager source files and run: "build_win.bat" to build binary and package it together with source into zip archive

