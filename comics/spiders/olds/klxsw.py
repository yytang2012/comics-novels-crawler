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

class KlxswSpider(scrapy.Spider):
    '''
    classdocs
    '''
    name = 'klxsw1';
    allowed_domains = ['www.klxsw1.com'];
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
        title = sel.xpath('//h1/a/text()').extract()[0]
        title = "%s-%s"%(title, self.name);
        title = self.polishString(title);
        print(title)
        tmpNovelDirPath = os.path.join(self.tmpDirPath, title);
        if(os.path.isdir(tmpNovelDirPath) != True):
            os.makedirs(tmpNovelDirPath);
        
        dd = sel.xpath('//div[@align="left"]/a');
        id = 0;        
        for d in dd:
            id += 1;
            url = d.xpath('@href').extract()[0];
            url = response.urljoin(url.strip());
            subtitle = d.xpath('text()').extract()[0];
            subtitle = self.polishString(subtitle);
            subtitle = '\n\n*********   ' + subtitle + '   *********\n\n';
            print(url);
            print(subtitle);
            request = scrapy.Request(url, callback = self.parse_page);
            item = NovelsItem();
            item['title'] = title;
            item['subtitle'] = subtitle;
            item['id'] = id;
            item['type'] = 'novels';
            request.meta['item'] = item;
            if(self.isFileExist(title, id) == False):
                yield request;
            else:
                pass;
    
    def isFileExist(self, title, id):
        tmpDirPath = settings['TMP_DIR'];
        tmpNovelDirPath = os.path.join(tmpDirPath, title);
        novelPath = os.path.join(tmpNovelDirPath, str(id)+'.txt');
        if(os.path.isfile(novelPath) == True):
            return True;
        else:
            return False;
    
    def parse_page(self, response):
        item = response.meta['item'];
        sel = Selector(response);
        content1 = sel.xpath('//div[@id="r1c"]/text()').extract();
        content = [];
        for cc in content1:
            content.append(cc+'\n\n');
        item['content'] = content;
        return item;
        
    
    
    
    
    
    
    
    
    