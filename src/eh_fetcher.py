# ! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import hashlib
import time

import requests
import json
from bs4 import BeautifulSoup

import decompressor

class EHFetcher():
    def __init__(self, manager):
        self.manager = manager
        self.temppath = self.manager.temppath
        
    def getEHError(self, html):
        """
        Returns
            0 - if no error
            1 - if html is overload error message
            2 - if html is banned message
            3 - if html is undefined error message
        """
        soup = BeautifulSoup(html)
        
        div_first = soup.body.find('div')
        if div_first is None:
            # no div in whole html == banned
            return 2
        
        divs = div_first.findAll('div')
        if divs == []:
            # its not error div
            return 0
        
        err = 0
        if divs[0].text.strip() == 'An Error Has Occurred':
            err = 3
            if divs[1].text.strip().startswith('You are opening pages too fast'):
                err = 1
            
        return err
    
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
    
    # TODO - exhentai search
    def searchEHByFileHash(self, img_file_sh1_hash):
        """
        Returns list of galleries on EH that have file with given sha1 hash
        """
        r = requests.get('http://g.e-hentai.org/?f_shash='+img_file_sh1_hash)
        html = unicode(r.text).encode("utf8")
        
        return self.getListOfEHGalleriesFromHTML(html)
        
    def getListOfEHGalleriesFromHTML(self, html):
        """
        Parses utf-8 encoded HTML with EH search result to list of galleries.
        Returns:
            result_list - list of EH galleries
            err - getEHErrors
        """
        # Test for html error
        err = self.getEHError(html)
        if err!=0:
            return [], err
        
        
        soup = BeautifulSoup(html)
        
        table_itg = soup.body.find('table', attrs={'class':'itg'})
        
        if table_itg is None:
            logger.debug('No gallery with same file found on EH')
            return [], err
        else:
            result_html_list = table_itg.findAll('tr')[1:]
                
        result_list = []
        for r in result_html_list:
            tds = r.findAll('td')
            
            if len(tds)<3:
                logger.warning('Bad TR: '+str(tds.text))
                continue
            
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
        
        return result_list, err

    def infoFromEHentaiLink(self, ehlink):
        """
        if HTML gets error uses EH API (doesnt have namespaces)
        Returns:
            result - ehentai.org gallery metdata from gallery link.
            err - error codes from:
                        getEHError
                        infoFromEHentai_API
                        infoFromEHentai_HTML
        
        posted - UNIX timestamp of uploading file to EH
        published - UNIX timestamp of adding fileinfo to database (local)
        """
        result, err = self.infoFromEHentai_HTML(ehlink)
        
        # if html is not accesable - fallback to API
        if err==11:
            # less ban
            time.sleep(4)
            
            index = ehlink.find('hentai.org/g/')
            splited = ehlink[(index+13):].split('/')
            
            gallery_id = splited[0]
            gallery_token = splited[1]
            
            logger.debug('EH id - '+str(gallery_id)+' token - '+str(gallery_token))
            
            result, err = self.infoFromEHentai_API(gallery_id, gallery_token)
        
        return result, err
        
    def infoFromEHentai_API(self, gallery_id, gallery_token):
        """
        Returns:
            ehentai.org gallery metadata from gallery_id and gallery_token.
            err:
                20 - if no API error
                21 - if API error
        http://ehwiki.org/wiki/API
        """
        err = 20
        payload = json.dumps({'method': 'gdata', 'gidlist': [[gallery_id, gallery_token]]})
        headers = {'content-type': 'application/json'}
        
        r = requests.post("http://g.e-hentai.org/api.php", data=payload, headers=headers)
        try:
            gallery_info = r.json()['gmetadata'][0]
        except:
            logger.error('Error connecting to EH API')
            gallery_info = []
            err = 21
        else:
            gallery_info['tags'] = {'misc':gallery_info['tags']}
            gallery_info['category'] = gallery_info['category'].lower()
        
        return gallery_info, err
        
    def infoFromEHentai_HTML(self, ehlink):
        """
        Returns:
            ehentai.org gallery metadata parsed from html file.
            err:
                getEHError codes
                11 - no gallery info accesable (gallery on exhentai)
        """
        r = requests.get(ehlink)
        html = unicode(r.text).encode("utf8")
        
        # Test for html error
        err = self.getEHError(html)
        if err!=0:
            return {}, err
        
        if len(html)<5000:
            logger.warning("Length of HTML response is only %s => Failure", str(len(html)))
            return {}, 11
            
        fileinfo = {}
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

        return fileinfo, err
