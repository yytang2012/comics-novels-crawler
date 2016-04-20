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

class Lewen8Spider(scrapy.Spider):
    '''
    classdocs
    '''
    name = 'lewen8';
    allowed_domains = ['www.lewen8.com'];
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
        ss = sel.xpath('//title/text()').extract()[0]
        pattern = re.compile(u'([^全文阅读]*)全文阅读');
        title= re.match(pattern,ss).group(1); 
        title = "%s-%s"%(title, self.name);
        title = self.polishString(title);
        print(title)
        tmpNovelDirPath = os.path.join(self.tmpDirPath, title);
        if(os.path.isdir(tmpNovelDirPath) != True):
            os.makedirs(tmpNovelDirPath);
        
        dd = sel.xpath('//ul[@class="chapterlist"]/li/a');
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
        content = sel.xpath('//div[@id="content"]/text()').extract();
        item['content'] = content;
        return item;
        
    
    
    
    
    
    
    
    
    