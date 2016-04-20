#!/usr/bin/env python
# coding=utf-8
'''
Created on Dec 27, 2015

@author: yytang
'''

import scrapy;
from scrapy.selector import Selector;
from comics.items import ComicsItem;
from scrapy.conf import settings;
import re;
import os;
import urllib;
from urlparse import urljoin

class FzdmSpider(scrapy.Spider):
    name = '999comic';
    allowed_domains = ['www.999comic.com'];
    #start_urls = [
     #   'http://manhua.fzdm.com/27/'
    #]
    urlPrefix = r'http://i.seemh.com:88'
    title = u'艳色灰姑娘';
    
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
        request = scrapy.Request(response.url, callback = self.parse_page);
        request.meta['title'] = self.title;
        request.meta['subtitle'] = '01';
        yield request;
            
    def parse_page(self, response):
        title = response.meta['title'];
        subtitle = response.meta['subtitle'];
        
        sel = Selector(response);
        ss = sel.xpath('//script[@type="text/javascript"]/text()').extract()[0]
        
        ss = ss.replace('\n','');
        pattern = re.compile(u'.*fs\':\[(.*)\],\'fc')

        m = re.match(pattern, ss);
        if(m == None):
            print m;
        else:
            #print m.group(1)
            tt = "%s" %(m.group(1));
            tt = tt.replace("'", "")
            urls = tt.split(',')
            num = len(urls);
            for id in range(1, num + 1):
                item = ComicsItem();
                item['type'] = 'comics';
                url = urllib.quote(urls[id-1].encode('utf-8'), safe = '[]');
                url = urljoin(self.urlPrefix, url);
                print(url)
                tmpUrl = [];
                tmpUrl.append(url);
                item['image_urls'] = tmpUrl;
                item['image_name'] = "%s/%s/%03d.jpg" %(title, subtitle, id);  
                yield item;
        
        
        
        
        
        
        
        
        
        
        
        
        