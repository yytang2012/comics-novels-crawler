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
import re;
import os;

class RanwenSpider(scrapy.Spider):
    '''
    classdocs
    '''
    name = 'ranwen';
    allowed_domains = ['www.ranwen.org'];
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
            
    def polishString(self, s):
        """Return a safe directory name."""   
        return re.sub("[/\\\?\|<>:\"\*]","_",s).strip()
    
    def parse(self, response):
        sel = Selector(response);
        title = sel.xpath('//h1/text()').extract()[0]
        title = "%s-%s"%(title, self.name);
        title = self.polishString(title);
        print(title)
        tmpNovelDirPath = os.path.join(self.tmpDirPath, title);
        if(os.path.isdir(tmpNovelDirPath) != True):
            os.makedirs(tmpNovelDirPath);
        
        dd = sel.xpath('//dd/a');
        id = 0;        
        for d in dd:
            id += 1;
            url = d.xpath('@href').extract()[0];
            url = response.urljoin(url);
            subtitle = d.xpath('text()').extract()[0];
            subtitle = self.polishString(subtitle);
            subtitle = '\n\n*********   [%d] - %s   *********\n\n'% (id, subtitle);
            print(url);
            print(subtitle);
            request = scrapy.Request(url, callback = self.parse_page);
            item = NovelsItem();
            item['title'] = title;
            item['subtitle'] = subtitle;
            item['id'] = id;
            item['type'] = 'novels';
            request.meta['item'] = item;
            yield request;
            
    def parse_page(self, response):
        item = response.meta['item'];
        sel = Selector(response);
        content = sel.xpath('//div[@id="content"]/text()').extract();
        item['content'] = content;
        return item;
        
    
    
    
    
    
    
    
    
    