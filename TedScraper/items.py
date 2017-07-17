# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TedscraperItem(scrapy.Item):

    talk_title = scrapy.Field()
    talk_link = scrapy.Field()
    talk_topics = scrapy.Field()
    upload_date = scrapy.Field()
    langs = scrapy.Field()
    transcript = scrapy.Field()
    time = scrapy.Field()
