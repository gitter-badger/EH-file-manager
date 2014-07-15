# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import hashlib

import py7zlib
import rarfile
import zipfile

import requests
import json
from bs4 import BeautifulSoup

import decompressor

class EHFetcher():
    def __init__(self, manager):
        self.manager = manager
        self.temppath = self.manager.temppath
    
    def getHashOfFileInGallery(self, filepath): 
        """
        Input:
            filepath - absolute path to archive file with images
        Returns SHA-1 hash of file in the middle of gallery.
        Returns None if error
        """
        # clean temp dir
        self.manager.clearTemp()
        
        # open archive
        try:
            archive = decompressor.ArchiveFile(filepath)
        except:
            logger.warning('Error uncompressing File: %s', filepath)
            return None
        
        # get list of files in archive
        filelist = archive.namelist()
        
        # filter out files that are not images
        filtered_filelist = []
        for f in filelist:
            if f.lower().split('.')[-1] in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
                filtered_filelist.append(f)

        # get path to page in the middle of file
        filtered_filelist.sort()
        file_to_use = filtered_filelist[int(len(filtered_filelist)/2)]
        
        # extract page
        archive.extract(file_to_use, self.temppath)
        archive.close()
            
        # get correct unix path to extracted file
        filepathlist = []
        for root, dirs, files in os.walk(self.temppath):
            paths = [os.path.join(root,f) for f in files]
            filepathlist+=paths
        file_to_use = filepathlist[0]
        old_path = os.path.join(self.temppath, file_to_use)
        
        # get SHA1 hash
        afile = open(old_path, 'rb')
        buf = afile.read()
        afile.close()
        hasher = hashlib.sha1()
        hasher.update(buf)
        sha1hash = hasher.hexdigest()
        
        # clean temp dir
        self.manager.clearTemp()
        
        return sha1hash
    
    def searchEHByFileHash(self, img_file_sh1_hash):
        """
        Returns list of galleries on EH that have file with given sha1 hash
        """
        r = requests.get('http://g.e-hentai.org/?f_shash='+img_file_sh1_hash)
        html = unicode(r.text).encode("utf8")
        
        return self.getListOfEHGalleriesFromHTML(html)
    
    # TODO - doesnt return some galleries (very perverted?) If not logged in !!!!
    def searchEHByName(self, name):
        name = name.replace(',','')
        args = {'f_search': name}
        r = requests.get('http://g.e-hentai.org/', params=args)
        html = unicode(r.text).encode("utf8")
        
        return self.getListOfEHGalleriesFromHTML(html)
        
    def getListOfEHGalleriesFromHTML(self, html):
        """
        Parses utf-8 encoded HTML with EH search result to list of galleries.
        """
        soup = BeautifulSoup(html)
        
        table_itg = soup.body.find('table', attrs={'class':'itg'})
        
        if table_itg is None:
            logger.debug('No gallery with same file found on EH')
            return []
        else:
            result_html_list = table_itg.findAll('tr')[1:]
                
        result_list = []
        for r in result_html_list:
            tds = r.findAll('td')
            
            # skip adds
            if tds[0].find('img') is None:
                continue
                        
            category = tds[0].find('img').get('alt').lower().strip()
            published = tds[1].text.strip()
            uploader = tds[3].text.strip()
            
            name_div = tds[2].find('div', attrs={'class':'it5'})

            gallery_name = name_div.text.strip()
            gallery_url = name_div.find('a').get('href')
            
            result_list.append([category, published, gallery_name, gallery_url, uploader])
        
        return result_list

    def infoFromEHentaiLink(self, ehlink):
        """
        Returns ehentai.org gallery metdata from gallery link.
        if HTML gets error uses EH API (doesnt have namespaces)
        """
        result = self.infoFromEHentai_HTML(ehlink)
        
        if result is None:
            index = ehlink.find('hentai.org/g/')
            splited = ehlink[(index+13):].split('/')
            
            gallery_id = splited[0]
            gallery_token = splited[1]
            
            logger.debug('EH id - '+str(gallery_id)+' token - '+str(gallery_token))
            
            return self.infoFromEHentai_API(gallery_id, gallery_token)
        else:
            return result
        
    def infoFromEHentai_API(self, gallery_id, gallery_token):
        """
        Returns ehentai.org gallery metadata from gallery_id and gallery_token.
        http://ehwiki.org/wiki/API
        """
        payload = json.dumps({'method': 'gdata', 'gidlist': [[gallery_id, gallery_token]]})
        headers = {'content-type': 'application/json'}
        
        r = requests.post("http://g.e-hentai.org/api.php", data=payload, headers=headers)
        gallery_info = r.json()['gmetadata'][0]
        
        gallery_info['tags'] = {'misc':gallery_info['tags']}
        gallery_info['category'] = gallery_info['category'].lower()
        
        return gallery_info 
        
    def infoFromEHentai_HTML(self, ehlink):
        """
        Returns ehentai.org gallery metadata parsed from html file.
        """
        fileinfo = {}
        
        r = requests.get(ehlink)
        html = unicode(r.text).encode("utf8")
        if len(html)<5000:
            logger.warning("Length of HTML response is only %s => Failure", str(len(html)))
            return None
        soup = BeautifulSoup(html)

        div_gd2 = soup.body.find('div', attrs={'id':'gd2'})
        fileinfo['title'] = div_gd2.find('h1', attrs={'id':'gn'}).text
        fileinfo['title_jpn'] = div_gd2.find('h1', attrs={'id':'gj'}).text

        div_gd3 = soup.body.find('div', attrs={'id':'gd3'})
        fileinfo['category'] = div_gd3.find('img').get('alt')

        left_text = div_gd3.find('div', attrs={'id':'gdd'}).text
        fileinfo['language'] = left_text[left_text.find('Language:')+9:]

        div_gd4 = soup.body.find('div', attrs={'id':'gd4'})
        div_taglist = div_gd4.find('div', attrs={'id':'taglist'}).find_all('tr')
        fileinfo['tags'] = {}
        for tl in div_taglist:
            tds = tl.find_all('td')
            cat = tds[0].text[:tds[0].text.find(':')]
            tags = [t.text for t in tds[1].find_all('a')] 
            
            fileinfo['tags'][cat] = tags

        return fileinfo
