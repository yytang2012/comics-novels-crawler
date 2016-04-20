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
import PyV8;

class FzdmSpider(scrapy.Spider):
    name = 'seemh';
    allowed_domains = ["tw.seemh.com", "www.seemh.com", "ccache.duapp.com"];
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
        title = sel.xpath('//h1/text()').extract()[0];
        aa = sel.xpath('//li/a[@class="status0"]')
        for a in aa:
            subtitle = a.xpath('@title').extract()[0];
            url = a.xpath('@href').extract()[0];
            url = response.urljoin(url);
            request = scrapy.Request(url, callback = self.parse_page_one);
            request.meta['title'] = '%s/%s' %(title, subtitle);
            yield request;
       
    
    def parse_page_one(self, response):
        title = response.meta['title'];
        
        html = response.body
        info_eval = re.search(r'<script type="text/javascript">(eval[^<]+)', html).group(1);
        
        #configjs_url = re.search( r'src="(http://[^"]+?/config_\w+?\.js)"', html).group(1)
        #print configjs_url;
        #request = scrapy.Request(configjs_url, callback = self.parse_page_two);
        refUrl = response.url;

        f = open("/home/yytang/programming/python/comics/comics/spiders/config_seemh.js", "rb");        
        configjs = f.read();
        #print configjs_url;
        #response = urllib2.urlopen(configjs_url);
        #configjs = response.read();
        crypto = re.search(r"(var CryptoJS.+?)var pVars", configjs, re.S).group(1)
        #print crypto;        
        
        """ run javascript """
        ctxt = PyV8.JSContext();
        ctxt.enter();
        ctxt.eval(crypto + info_eval);
        files, path = ctxt.eval("[cInfo.files, cInfo.path]")        
        urls = ["http://i.seemh.com:88" + path + file for file in files];
        
        id = 0;
        for url in urls:
            id += 1;
            imgName = "%s/%03d.jpg" %(title, id);  
            imgPath = os.path.join(settings['IMAGES_STORE'], imgName);
            if os.path.isfile(imgPath):
                continue;
            item = ComicsItem();
            item['type'] = 'comics';
            tmpurl = [];
            tmpurl.append(url);
            item['image_urls'] = tmpurl;
            item['Referer'] = refUrl;            
            item['image_name'] = imgName;
            yield item;
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        