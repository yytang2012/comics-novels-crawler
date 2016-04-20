#!/usr/bin/env python
# coding=utf-8

import scrapy;
from scrapy.selector import Selector;
from comics.items import ComicsItem;
from scrapy.conf import settings;
import re;
import os;

class Ck101Spider(scrapy.Spider):
    name = 'ck101';
    allowed_domains = ['comic.ck101.com'];
    #start_urls = [
     #   'http://manhua.fzdm.com/27/'
    #]
    #URLS = re.compile(r'index_[\d]{1,3}\.html');
    title = '';
    outputDir = settings['IMAGES_STORE'];
    
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
        #url = "http://manhua.fzdm.com/132/63/";        
        sel = Selector(response);        
        dd = sel.xpath('//div[@class="relativeRec"]')[-1];
        urls = dd.xpath('ul/li/a/@href').extract();
        for url in urls:
            url = response.urljoin(url);
            request = scrapy.Request(url, callback = self.parse_page);
            yield request;          

    def parse_page(self, response):
        sel = Selector(response);  
        title = sel.xpath('//title/text()').extract()[0].strip();   
        title = title.replace('/', '-');   
        subtitle = sel.xpath('//h2/strong/text()').extract()[0].strip();
        subtitle = subtitle.replace('/', '-');
        
        updateOnly = False;
        if (settings['ACTION'] == 'UPDATE_ONLY'):
            updateOnly = True;
        if(updateOnly == True):
            subDir = "%s/%s" %(title, subtitle);
            subDirPath = os.path.join(self.outputDir, subDir);
            if(os.path.isdir(subDirPath) == True):
                print("%s was downloaded" % subtitle);
                return ;                
            else:
                print("update chapter %s" %(subtitle))
            
        pattern = re.compile(r'(.*)/\d+');
        urlPrefix = re.match(pattern, response.url).group(1);
        num = len(response.xpath('//option'));
        
        # page 1
        itemOne = ComicsItem();
        itemOne['type'] = 'comics';
        itemOne['image_name'] = "%s/%s/%03d.jpg" %(title, subtitle, 1);
        itemOne['image_urls'] = sel.xpath("//img[@id = 'defualtPagePic']/@src").extract();

        for id in range(2, num+1):
            url = "%s/%d" %(urlPrefix, id);
            item = ComicsItem();
            item['type'] = 'comics';
            #item['image_name'] = "%d" %(id); 
            item['image_name'] = "%s/%s/%03d.jpg" %(title, subtitle, id);
            item['image_urls'] = [];
            items = [];
            request = scrapy.Request(url, callback = self.parse_page2);
            if(id == 2):
                items.append(itemOne);
            request.meta['item'] = item;
            request.meta['items'] = items;
            yield request;        

    def parse_page2(self, response):
        sel = Selector(response);        
        item = response.meta['item'];
        items = response.meta['items'];
        image_urls = sel.xpath("//img[@id = 'defualtPagePic']/@src").extract();
        item['image_urls'] = image_urls;
        items.append(item);
        return items;
        
        
        
