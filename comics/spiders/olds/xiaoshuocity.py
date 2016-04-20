#!/usr/bin/env python
# coding=utf-8
'''
Created on Dec 24, 2015

@author: yytang
'''

import scrapy;
from scrapy.selector import Selector;
from scrapy.conf import settings;
from comics.items import NovelsItem;
import re;
import os;

class XiaoshuocitySpider(scrapy.Spider):
    '''
    classdocs
    '''
    name = 'xiaoshuocity';
    allowed_domains = ['www.xiaoshuocity.com'];
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
        title = sel.xpath('//h2/text()').extract()[0]
        title = "%s-%s"%(title, self.name);
        title = self.polishString(title);
        print(title)
        tmpNovelDirPath = os.path.join(self.tmpDirPath, title);
        if(os.path.isdir(tmpNovelDirPath) != True):
            os.makedirs(tmpNovelDirPath);
        
        dd = sel.xpath('//ul/li/a');
        id = 0;        
        for d in dd:
            id += 1;
            url = d.xpath('@href').extract()[0];
            url = response.urljoin(url);
            subtitle = d.xpath('text()').extract()[0];
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
        content1 = sel.xpath('//div[@class="content"]/p/text()').extract();
        content = [];
        for cc in content1:
            content.append(cc+'\n');
        item['content'] = content;
        return item;
        
    
    
    
    
    
    
    
    
    