# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ComicsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    image_name = scrapy.Field();
    image_urls = scrapy.Field();
    type = scrapy.Field();
    Referer = scrapy.Field();

class NovelsItem(scrapy.Item):
    type = scrapy.Field();
    title = scrapy.Field();
    subtitle = scrapy.Field();
    content = scrapy.Field();
    id = scrapy.Field();
    
class NovelsInfo(scrapy.Item):
    type = scrapy.Field();
    title = scrapy.Field();
    url = scrapy.Field();
    author = scrapy.Field();
    date = scrapy.Field();