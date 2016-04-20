#!/usr/bin/env python
# coding=utf-8

import scrapy;
from scrapy.selector import Selector;
from comics.items import ComicsItem;
from scrapy.conf import settings;
import re;
import os;

class FzdmSpider(scrapy.Spider):
    name = 'fzdm';
    allowed_domains = ['manhua.fzdm.com'];
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
        updateOnly = False;
        if (settings['ACTION'] == 'UPDATE_ONLY'):
            updateOnly = True;
        sel = Selector(response);
        ss = sel.xpath('//title/text()').extract()[0]
        pattern = re.compile(u'([^漫画]*)漫画');
        tt= re.match(pattern,ss).group(1); 
        self.title = "%s"%tt;
        print(self.title)
        
        aa = sel.xpath('//li[@class="pure-u-1-2 pure-u-lg-1-4"]/a');
        for a in aa:
            #url = a.xpath('@href').extract();
            url = response.urljoin(a.xpath('@href').extract()[0]);
            subtitle = a.xpath('@title').extract()[0];
#            print(url);
 #           print(subtitle)
            if(updateOnly == True):
                subDir = "%s/%s" %(self.title, subtitle);
                subDirPath = os.path.join(self.outputDir, subDir);
                if(os.path.isdir(subDirPath) == True):
                    print("%s was downloaded" % subtitle);
                    continue;                
                else:
                    print("update chapter %s" %(subtitle))
            request = scrapy.Request(url, callback = self.parse_page);
            request.meta['flag'] = True;
            request.meta['subtitle'] = subtitle;
            request.meta['id'] = 1;
            request.meta['items'] = [];
            yield request;

    def parse_page(self, response):
        flag = response.meta['flag'];
        subtitle = response.meta['subtitle'];
        id = response.meta['id'];
        items = response.meta['items'];

        sel = Selector(response);
        sites = sel.xpath('//img[@id="mhpic"]');
        image_urls = sites.xpath('@src').extract();
        print("url = %s" %image_urls);
        item = ComicsItem();
        item['type'] = 'comics';
        item['image_urls'] = image_urls;
        #item['image_name'] = "%d" %(id); 
        item['image_name'] = "%s/%s/%03d.jpg" %(self.title, subtitle, id);         
        imagePath = os.path.join(self.outputDir, item['image_name']);
        print(imagePath +"************")
        if(os.path.isfile(imagePath) != True):
            items.append(item);
        else:
            print("%s was downloaded" %(item['image_name']));
            
        if(flag == True):
            start = False;
            reqs = [];
            sites = sel.xpath('//a');
            for site in sites:
                contents = site.xpath('text()').extract();
                if(len(contents) == 0):
                    continue;
                else:
                    content = contents[0];
                if( site.xpath('@id').extract() != [] ):
                    pattern = re.compile(u'第\d+页');
                    if(pattern.match(content)):
                        start = True;
                        print("Start!!!");
                        continue;
                    elif (start == True):
                        start = False;
                        print("Stop!!!");
                if( start == False ):
                    continue;
                url = site.xpath('@href').extract();
                pattern = re.compile(r'index_\d+\.html');
                if(len(url) != 0 and pattern.match(url[0])):
                    weburl = response.urljoin(url[0]);
                    print(weburl);
                    print(content);
                    request = scrapy.Request(weburl, callback = self.parse_page);
                    request.meta['flag'] = False;
                    request.meta['subtitle'] = subtitle;
                    request.meta['id'] = int(content);
                    request.meta['items'] = [];
                    reqs.append(request);
            if(len(reqs) != 0):
                reqs[-1].meta['flag'] = True;
                reqs[0].meta['items'] = items;
                return reqs;
        return items;

