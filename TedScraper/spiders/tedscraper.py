# -*- coding: utf-8 -*-

import scrapy
from TedScraper.items import TedscraperItem


class TedscraperSpider(scrapy.Spider):
    name = 'tedscraper'
    allowed_domains = ['www.ted.com/talks']
    start_urls = ['https://www.ted.com/talks']

    elements = {
        'talk_links': 'div.talk-link h4 a.ga-link::attr("href")',
        'talk_title': 'string(//meta[@name="title"]/@content)',
        'talk_topics': '//meta[@property="video:tag"]/@content',
        'upload_date': 'string(//meta[@itemprop="uploadDate"]/@content)',
        'langs': '//link[@rel="alternate"]/@hreflang',
        'transcript': 'div.Grid--with-gutter.p-b\:4 p::text',
    }

    def parse(self, response):

        urls = response.css(self.elements['talk_links']).extract()
        for url in urls:
            # print("target url: {}".format(response.urljoin(url)))
            yield scrapy.Request(response.urljoin(url), self.parse_talks, dont_filter=True)

    def parse_talks(self, response):

        item = TedscraperItem()
        item['talk_title'] = response.xpath(self.elements['talk_title']).extract_first()
        item['talk_link'] = response.url
        item['talk_topics'] = response.xpath(self.elements['talk_topics']).extract()
        item['upload_date'] = response.xpath(self.elements['upload_date']).extract_first()
        item['langs'] = response.xpath(self.elements['langs']).extract()

        item['transcript'] = {}
        for lang in item['langs']:
            transcript_abs_url = '{}/transcript?language={}'.format(response.url, lang)

            transcript_url = response.urljoin(transcript_abs_url)
            print("transcript url: {}".format(transcript_url))

            transcript = scrapy.Request(transcript_url, callback=self.parse_transcript)
            item['transcript'][lang] = transcript

        yield item

    def parse_transcript(self, response):
        print("CALLED")
        print(response.css(self.elements['transcript']).extract())
        print("response body: {}".format(response.body))
        print(type(response.css(self.elements['transcript']).extract()))

        yield response.css(self.elements['transcript']).extract()
