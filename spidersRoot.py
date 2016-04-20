'''
Created on Dec 23, 2015

@author: yytang

Description:
The Goal of this python script is to crawl images and novels. the script will implement the following steps:
1. Read the url from urlfile and check if this url is in database, if yes then skip this one, otherwise go to the next step.
2. Decide the url's domain and which spider to apply on.
3. Implement the spider.
4. Add the url and related infomation to database and Update the log.
'''

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from comics.spiders.fzdmSpider import FzdmSpider;
from scrapy.conf import settings;
import os;
import shutil;
import time;
import io, json;
import re;

domains = [
           "manhua.fzdm.com",
           "www.sto.cc",
           'www.pbtxt.com',
           'www.shubao2s.com',
           'www.shubao22.com',
           'www.ucxsw.com',
           'www.8wxs.com',
           'www.bitu.co',
           'www.qbxs8.net',
           'www.xiaoshuocity.com',
           'www.lewenxiaoshuo.com',
           'www.lwxs.com',
           'www.hebao8.com',
           'www.dzxsw.la',
           'quanben-xiaoshuo.com',
           'www.tlbbsfso.com',
           'www.shushuwu.net',
           'www.xitxt.com',
           "www.dz88.com",
           "www.ranwen.org",
           "rouwenxue.com",
           "m.feifantxt.com",
           "www.123yq.org",
           'www.klxsw.com',
           "www.lwxs520.com",
           "www.lwxsw.org",
           "www.biquge.la",
           "www.lewen8.com",
           "www.999comic.com",
           "comic.ck101.com",
           "www.177pic.info",
           "www.baishulou.net",
           'www.ybdu.com',
           "tw.seemh.com", "www.seemh.com"
        ];
reserveDoms = [
            "tw.seemh.com", "www.seemh.com"
        ];
"""
spidersDic = {
              "manhua.fzdm.com": "fzdm",
              "www.sto.cc" : "sto",
              "www.biquge.la" : "biquge",
              "www.baishulou.net" : "baishulou",
              "www.lewen8.com" : "lewen",
              "www.999comic.com" : "comics999",
              "comic.ck101.com" : "ck101",
              "www.177pic.info" : "comics177"
              };
"""
clearUrls = False;

def getSpiderName(url):
    pattern = re.compile(r'([^.]+)\.([^.]+)');
    m = re.search(pattern, url);
    p1 = m.group(1)
    p2 = m.group(2)
    if p2 == 'com':
        return p1;
    else:
        return p2;

def combinPieceToNovel(rootDir, outputDir):
    novels = [];
    for title in os.listdir(rootDir):
        novelDir = os.path.join(rootDir, title);   
        if(os.path.isfile(novelDir) == True):
            os.remove(novelDir);
            continue;     
        outputPath = os.path.join(outputDir, title + '.txt');
        files = os.listdir(novelDir);
        num = len(files);
        print(novelDir);
        # check if the novel integrity 
        isGood = True;
        id = 1;
        #print(files);
        print(num);
        #while(id <= num):
        for id in range(1, num + 1):
            filepath = os.path.join(novelDir, str(id) + '.txt');
            if(os.path.isfile(filepath) == False):
                isGood = False;
                print('Failed downloading page %d' %id);
                break;
            #print(id);
        if(isGood == False):
            continue;
        
        ofd = open(outputPath, 'w');
        for id in range(1, num + 1):
            filepath = os.path.join(novelDir, str(id) + '.txt');
            fd = open(filepath, 'r');
            for line in fd.readlines():
                ofd.write(line);
            fd.close();
        ofd.close();
        shutil.rmtree(novelDir);
        novels.append(title);
    return novels;
        
def updateLog(logPath, novels):
    #update the history log
    hfd = open(logPath, 'a');
    curTime = time.strftime('%Y-%m-%d %X', time.localtime())
    head = "+++++++++++++++++++++++++   " + curTime + "   ++++++++++++++++++++++++++\n";
    hfd.write(head);
    
    for title in novels:  
        ss = "\t%s\n" %title;
        hfd.write(ss);
    hfd.write('\n');
    hfd.close();

if __name__ == '__main__':    
    # Step 1: get the urls from urlfile
    urlPath = settings['URLFILE'];
    ufd = open(urlPath, 'r');
    urls = ufd.readlines();
    ufd.close();
    urlsOutput = [];
    
    # if urlfile is empty, use the url from weburl variable.
    if(len(urls) == 0):
        print('urlfile is empty');
        #exit;
    
    # recreate the temporary directory
    tmpDirPath = settings['TMP_DIR'];
    if(os.path.isdir(tmpDirPath) == False):
        os.makedirs(tmpDirPath);    
    
    # check if the url is supported
    isBusy = False;
    for url in urls:
        for dom in domains:
            if(dom in url):
                isBusy = True;
                spiderName = getSpiderName(dom);
                mUrlPath = os.path.join(tmpDirPath, spiderName);
                print(spiderName);
                print(mUrlPath);
                fd = open(mUrlPath, 'a');
                fd.write(url);
                fd.close();
                if(dom in reserveDoms):
                    urlsOutput.append(url);
                #continue;                
                
    if(isBusy == True):
        process = CrawlerProcess(get_project_settings()) 
        for dom in domains:
            spiderName = getSpiderName(dom);
            mUrlPath = os.path.join(tmpDirPath, spiderName);
            if(os.path.isfile(mUrlPath) == True):                
                # 'followall' is the name of one of the spiders of the project.
                process.crawl(spiderName, domain = dom)               
        process.start() # the script will block here until the crawling is finished

    novelsDir = settings['NOVELS_DIR'];
    """
    for dom in domains:
        spiderName = spidersDic[dom];
        jsonPath = os.path.join(tmpDirPath, spiderName + ".json");
        if(os.path.isfile(jsonPath) == True):
            with io.open(jsonPath, 'r', encoding='utf-8') as fd:
                jsons = json.load(fd);
                print(jsons);
    """
    novels = combinPieceToNovel(tmpDirPath, novelsDir);
    logPath = settings['LOGFILE']
    updateLog(logPath, novels);
    
    if clearUrls == True:
        ufd = open(urlPath, 'w');
        for url in urlsOutput:
            ufd.write(url);
        ufd.close();
        print("urlfile has been cleared");
                
                
                
                
                
                
                
                
                
    