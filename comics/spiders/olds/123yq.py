#!/usr/bin/env python
# coding=utf-8
'''
Created on Jan 23, 2016

@author: yytang
'''

import scrapy;
from scrapy.selector import Selector;
from scrapy.conf import settings;
from comics.items import NovelsItem;
from polish import *;
import re;
import os;

class Yq123Spider(scrapy.Spider):
    '''
    classdocs
    '''
    name = '123yq';
    allowed_domains = ['www.123yq.org'];
    tmpDirPath = settings['TMP_DIR'];
    
    def start_requests(self):
        #lewenUrlPath = settings['LEWEN_NOVELS_URLFILE'];
        urlPath = os.path.join(self.tmpDirPath, self.name);
        fd = open(urlPath, 'r');
        urls = fd.readlines();
        fd.close(); 
        for url in urls:
            url = url.strip('\n').strip();
            yield self.make_requests_from_url(url);
            
    
    def parse(self, response):
        sel = Selector(response);
        title = sel.xpath('//h1/text()').extract()[0]
        title = polishTitle(title, self.name);
        print(title)
        tmpNovelDirPath = os.path.join(self.tmpDirPath, title);
        if(os.path.isdir(tmpNovelDirPath) != True):
            os.makedirs(tmpNovelDirPath);
        
        dd = sel.xpath('//dl/dd');
        id = 0;        
        for d in dd:
            id += 1;
            nid = ((id-1)/3+1)*3 - (id-1)%3;
            a = d.xpath('a');
            if(len(a) == 0):
                continue;
            url = a.xpath('@href').extract()[0];
            url = response.urljoin(url.strip());
            subtitle = a.xpath('text()').extract()[0];
            subtitle = polishSubtitle(subtitle);
            print(url);
            print(subtitle);
            request = scrapy.Request(url, callback = self.parse_page);
            item = NovelsItem();
            item['title'] = title;
            item['subtitle'] = subtitle;
            item['id'] = nid;
            item['type'] = 'novels';
            request.meta['item'] = item;
            yield request;
            
    def parse_page(self, response):
        item = response.meta['item'];
        sel = Selector(response);
        content = sel.xpath('//div[@class="zhangjieTXT"]/text()').extract();
        item['content'] = content;
        return item;
        
    
    
    
    
    
    
    
    
    