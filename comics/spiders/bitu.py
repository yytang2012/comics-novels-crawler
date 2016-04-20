#!/usr/bin/env python
# coding=utf-8
'''
Created on Jan 20, 2016

@author: yytang
'''

import scrapy;
from scrapy.selector import Selector;
from scrapy.conf import settings;
from comics.items import NovelsItem;
from polish import *;
import re;
import os;

class BituSpider(scrapy.Spider):
    '''
    classdocs
    '''
    name = 'bitu';
    allowed_domains = ['www.bitu.co'];
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
        
        dd = sel.xpath('//div[@class="list"]/ul/li/a');
        pages = polishPages(title, len(dd));
        for i in pages:
            d = dd[i-1];
            url = d.xpath('@href').extract()[0];
            url = response.urljoin(url.strip());
            subtitle = d.xpath('text()').extract()[0];
            subtitle = polishSubtitle(subtitle);
            print(url);
            print(subtitle);
            request = scrapy.Request(url, callback = self.parse_page);
            item = NovelsItem();
            item['title'] = title;
            item['subtitle'] = subtitle;
            item['id'] = i;
            item['type'] = 'novels';
            request.meta['item'] = item;
            yield request;
    
    def parse_page(self, response):
        item = response.meta['item'];
        sel = Selector(response);
        content = sel.xpath('//div[@class="chapter"]/text()').extract();
        content = polishContent(content);
        item['content'] = content;
        return item;
        
    
    
    
    
    
    
    
    
    