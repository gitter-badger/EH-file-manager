EH file manager
======
The goal of this little project it to create a manga managment system that could be fully used as off-line version of e-hentai.org gallery system.

The main reason why was this project started, is that even though EH gallery system is very good at showing you what you want to find, its very hard to find the something in the heap of downloaded files you get after browsing the site for a while.

Install
-------
To get current development:

    git clone https://github.com/kunesj/EH-file-manager.git

Required dependencies on Linux Ubuntu/Mint 13.10:

    sudo apt-get install python python-pip python-sqlite python-qt4 mcomix
    sudo pip install requests beautifulsoup4
    
License
-------
GPL2 - GNU GENERAL PUBLIC LICENSE, Version 2

https://www.gnu.org/licenses/gpl-2.0.txt

Changelog
---------
0.2

- Changed name to "EH file manager"
- GUI for editing file info 
- Nicer looking file details 
- Automatically find new files in gallery and add them to database
- Mark new files in database
- Settings file (reader, categories, namespaces)
- GUI for editing settings 
- Better Japanese support 
- Searching by filehash, new files, deleted files
- File status (new/deleted) in filelist

0.1

- First release
