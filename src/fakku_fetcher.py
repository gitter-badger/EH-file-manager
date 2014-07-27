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

import time
import dateutil.parser as dateparser

import requests
from bs4 import BeautifulSoup

class FakkuFetcher():
    def __init__(self):
        pass
        
    def infoFromFakkuLink(self, fakkulink):
        """
        Returns:
            fakku gallery metadata parsed from html file.
        """
        r = requests.get(fakkulink)
        html = unicode(r.text).encode("utf8")
            
        fileinfo = {}
        soup = BeautifulSoup(html)
        
        # category
        category_raw = soup.body.find('div', attrs={'class':'breadcrumbs'}).find('a').text.strip().lower()
        if category_raw == 'hentai manga':
            fileinfo['category'] = 'manga'
        elif category_raw == 'hentai doujinshi':
            fileinfo['category'] = 'doujinshi'
        else:
            fileinfo['category'] = 'misc'
        
        # get info div
        div_wrap = soup.body.find('div', attrs={'id':'content'}).find('div').find('div', attrs={'id':'right'}).find('div', attrs={'class':'wrap'})
        
        # title
        fileinfo['title'] = div_wrap.find('div', attrs={'class':'content-name'}).text.strip()
        
        # tags + other info
        fileinfo['tags'] = {}
        divs_row = div_wrap.find_all('div', attrs={'class':'row'})
        for r in divs_row:
            left =  r.find('div', attrs={'class':'left'}).text.strip().lower()
            
            if left in ['series', 'artist', 'translator', 'description', 'uploader', 'language']:
                right = r.find('div', attrs={'class':'right'}).text.strip().lower()
            elif left == 'tags':
                right = r.find('div', attrs={'class':'right tags'})
            elif left in ['pages', 'favorites']:
                logger.info('Skipping info category: '+str(left))
                continue
            else:
                logger.warning('Not defined info category: '+str(left))
                continue
            
            
            if left == 'series' and right != 'original work':
                fileinfo['tags']['parody'] = [right]
                
            elif left == 'artist':
                fileinfo['tags']['artist'] = [right]
                
            elif left == 'translator':
                fileinfo['translator'] = right
                
            elif left == 'language':
                fileinfo['tags']['language'] = [right]
                fileinfo['language'] = right
                
            elif left == 'uploader':
                uploader = right.split('on')[0].strip().lower()
                published = right.split('on')[1].strip()
                
                dt = dateparser.parse(published)
                published_unix = int(time.mktime(dt.timetuple()))
                
                fileinfo['uploader'] = uploader
                fileinfo['published'] = published_unix 
                
            elif left == 'description':
                if right=='no description has been written.':
                    fileinfo['description'] = ''
                else:
                    fileinfo['description'] = right
                    
            elif left == 'tags':
                tags_parased = []
                tags = right.find_all('a')
                for t in tags:
                    text = t.text.strip().lower()
                    if text != '+':
                        tags_parased.append(text)
                
                fileinfo['tags']['misc'] = tags_parased

        return fileinfo
        
if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    full_gallery_url = raw_input("Enter url of fakku gallery:\n")
    
    ff = FakkuFetcher()
    fileinfo = ff.infoFromFakkuLink(full_gallery_url)
    
    print fileinfo
