#!/usr/bin/env python
# coding=utf-8
'''
Created on Dec 25, 2015

@author: yytang
'''

import scrapy;
from scrapy.selector import Selector;
from comics.items import ComicsItem;
from scrapy.conf import settings;
import re;
import os;

class FzdmSpider(scrapy.Spider):
    name = '177pic';
    allowed_domains = ['www.177pic.info'];
    #start_urls = [
     #   'http://manhua.fzdm.com/27/'
    #]
    
    title = '';
    outputDir = settings['IMAGES_STORE2'];
    
    def start_requests(self):
        #comicsUrlPath = settings['COMICS_URLFILE'];
        tmpDirPath = settings['TMP_DIR'];
        comicsUrlPath = os.path.join(tmpDirPath, self.name);
        fd = open(comicsUrlPath, 'r');
        urls = fd.readlines();
        fd.close(); 
        for url in urls:
            url = url.strip('\n').strip();
            yield self.make_requests_from_url(url);
            
            
    def parse(self, response):
        sel = Selector(response);
        url = sel.xpath('//span[@class="single-navi"]/../@href').extract()[-1]
        pattern = re.compile(u'(.*)/([\d]+)$')
        m = re.match(pattern, url);
        prefixUrl = m.group(1);        
        maxPage = int(m.group(2));
        
        ss = sel.xpath('//h1/text()').extract()[0]
        ss = ss.replace(u'[中文]', '');
        pattern = re.compile(u'\[[^\]]*\](.*)') 
        title = re.match(pattern, ss).group(1);
        
        for page in range(1, maxPage + 1):
            url = prefixUrl + '/' + str(page);
            request = scrapy.Request(url, callback = self.parse_page);
            request.meta['title'] = title;
            request.meta['page'] = page;
            yield request;
        
    
    def parse_page(self, response):
        title = response.meta['title'];
        page = response.meta['page'];
        
        sel = Selector(response);
        imgUrls = sel.xpath('//img/@src').extract();
        num = len(imgUrls);
        for id in range(1, num + 1):
            item = ComicsItem();
            item['type'] = 'comics';
            tmpurl = [];
            tmpurl.append(imgUrls[id-1]);
            item['image_urls'] = tmpurl;
            #item['image_name'] = "%d" %(id); 
            item['Referer']=None;
            item['image_name'] = "%s/%03d.jpg" %(title, (page-1) * 10 + id);  
            yield item;
        
        
        
        
        
        
        
        
        
        
        
        
        
        