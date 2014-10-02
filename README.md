<h2> This is very alpha version, expect a lot of errors and regressions!! </h2>
That means that if you don't want to torture yourself, you shouldn't use it until this notice disappears.


EH File Manager
======
The goal of this little project it to create a file managment system that could be fully used as off-line version of e-hentai.org gallery system.

The main reason why was this project started, is that even though EH is very good at showing you what you want to find, its very hard to find something in the heap of downloaded files you get after browsing the site for a while.

Preview (v0.4): 
![ScreenShot](https://raw.github.com/kunesj/EH-file-manager/master/doc/preview.png)

Install
-------

See [install notes](https://github.com/kunesj/EH-file-manager/blob/master/INSTALL.md) for Linux and Windows

To get current development run:

    git clone https://github.com/kunesj/EH-file-manager.git
    
or just download zipped source from:

    https://github.com/kunesj/EH-file-manager
    
License
-------
GPL2 - GNU GENERAL PUBLIC LICENSE, Version 2

https://www.gnu.org/licenses/gpl-2.0.txt

Changelog
---------
0.4

- Fixed: file details moves filelist
- Fixed: e-hentai.org overload/ban problem
- Fixed: fixed requests hang (added 30s timeout)
- Fixed: settings [' '] bug
- Fixed: parsing gallery list from e-hentai.org when "tr" tag was add
- Fixed: crash when extraction / thumb generation failed
- Fixed: search - filtered files must now have all tags
- Enchacement: delay when searching or updating from e-hentai.org (default 2s)
- Enchacement: detect overload warning and wait when searching or updating from e-hentai.org (default 60s)
- Enchacement: login to e-hentai.org to gain acces to exhentai.org galleries
- Enchacement: save e-hentai.org cookies for autologin
- Enchacement: GUI - e-hentai.org login menu
- Enchacement: GUI - delay and overload delay in settings
- Enchacement: Runs on Windows (with some small problems)
- Enchacement: replaced md5 hash with sha1
- Enchacement: search by part of tag
- Enchacement: basic support for fakku.net links
- Enchacement: parsing description and published time from e-hentai.org
- Enchacement: filter search by OTHER category
- Enchacement: now uses system temp directory
- Enchacement: fix paths to files when they are moved or renamed
- Enchacement: More detailed install info for Linux and Windows

0.3

- Added thumbnail to file details
- Selectable text in file details
- Added publish time and description to file details
- GUI - find new files
- GUI - update search results from EH
- GUI - update from EH
- Search for fileinfo on EH by imagehash or name
- Option to automatically search EH when adding files
- Search - filter by categories
- Search - search by filename
- Search - sort search results (published, title, title jpn)
- Settings - added allowed file extensions, default enabled categories
- Context menu

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
