'''
Created on Mar 21, 2016

@author: yytang
'''
from scrapy.conf import settings;
import os;
import re;

def polishString(s):
    """Return a safe directory name."""   
    return re.sub("[/\\\?\|<>:\"\*]","_",s).strip()

def polishTitle(title, siteName):
    title = "%s-%s"%(title, siteName);
    title = polishString(title);
    return title;
    
def polishSubtitle(subtitle):
    subtitle = polishString(subtitle);
    subtitle = '\n*********   ' + subtitle.strip() + '   *********\n\n';
    return subtitle;

def polishPages(title, size):
    tmpDirPath = settings['TMP_DIR'];
    tmpNovelDirPath = os.path.join(tmpDirPath, title);
    pages = [];
    for i in range(1, size + 1):
        novelPath = os.path.join(tmpNovelDirPath, str(i)+'.txt');
        if(os.path.isfile(novelPath) == False):
            pages.append(i);
    print(pages);
    return pages;
    
def polishContent(content, num = 0):
    res = [];
    enters = '\n\n';
    for cc in content:
        if(cc.strip().strip('\r') == ''):
            continue;
        res.append(cc.strip('\n\r')+enters);
    return res;
    
    