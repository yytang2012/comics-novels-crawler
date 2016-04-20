#!/usr/bin/env python
# coding=utf-8

'''
Created on Dec 25, 2015

@author: yytang
'''

import scrapy;
from scrapy.selector import Selector;
from scrapy.conf import settings;
from comics.items import NovelsItem;
from comics.items import NovelsInfo;
import re;
import os;
import io;
import json;
from polish import *;

class StoSpider(scrapy.Spider):
    '''
    classdocs
    '''
    name = 'sto';
    allowed_domains = ['www.sto.cc'];
    tmpDirPath = settings['TMP_DIR'];
    length = 0;
    jsons = [];
    def start_requests(self):
        #lewenUrlPath = settings['LEWEN_NOVELS_URLFILE'];        
        urlPath = os.path.join(self.tmpDirPath, self.name);
        fd = open(urlPath, 'r');
        urls = fd.readlines();
        fd.close(); 
        self.length = len(urls);
        for url in urls:
            url = url.strip('\n').strip();
            yield self.make_requests_from_url(url);
        
    def updateJSON(self, url, title, author):
        # TODO ...
        jsonData = NovelsInfo();
        jsonData['type'] = "novels";
        jsonData['url'] = url;
        jsonData['title'] = title;
        jsonData['author'] = author;
        
        self.jsons.append(jsonData);
        print("length = %d, size = %d" %(len(self.jsons,), self.length));
        if(len(self.jsons) == self.length):
            print(self.jsons);
            jsonPath = os.path.join(self.tmpDirPath, self.name + ".json");  
            with io.open(jsonPath, 'w', encoding='utf-8') as fd:
                fd.write(unicode(json.dumps(self.jsons, sort_keys = True, indent = 4, ensure_ascii=False)))
                fd.close();

       # with io.open(outputPath, 'w', encoding='utf-8') as fd:
        #    fd.write(unicode(json.dumps(jsonData, sort_keys = True, indent = 4, ensure_ascii=False)))
            #json.dump(jsonData, fd, sort_keys = True, indent = 4, ensure_ascii=False)
          #  fd.write(unicode('\n'))
            
    def parse(self, response):
        sel = Selector(response);
        ss = sel.xpath('//h1/text()').extract()[0]
        pattern = re.compile(u'《([^》]*)》');
        title = re.match(pattern, ss).group(1);
        title = polishTitle(title, self.name);
        print(title)
        pattern = re.compile(u'.*：([^：]*)$')
        tt = re.match(pattern, ss).group(1);
        author = "%s"%tt;
        #self.updateJSON(response.url, title, author);
        tmpNovelDirPath = os.path.join(self.tmpDirPath, title);
        if(os.path.isdir(tmpNovelDirPath) != True):
            os.makedirs(tmpNovelDirPath);
        
        # Subtitle
        subtitle = '';
        
        # Get the last page number
        lastUrl = sel.xpath('//div[@id="webPage"]/a/@href').extract()[-1]
        pattern = re.compile(u'[^-]*-(\d+)/');
        maxPage = int(re.match(pattern, lastUrl).group(1));
        
        # Get the url prefix
        pattern = re.compile(u'([^-]*)');
        m = re.match(pattern, response.url);
        pageUrlPrefix = "%s-" %(m.group(0));
        
        for id in range(1, maxPage + 1):
            url = "%s%d" %(pageUrlPrefix, id);            
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
        content = sel.xpath('//div[@id="BookContent"]/text()').extract()
        content = content = polishContent(content);
        item['content'] = content;
        
        return item;
        