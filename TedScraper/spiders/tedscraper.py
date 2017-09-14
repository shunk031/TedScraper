# -*- coding: utf-8 -*-

from urllib.request import urlopen

import scrapy
from TedScraper.items import TedscraperItem
from bs4 import BeautifulSoup


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
            yield scrapy.Request(response.urljoin(url), self.parse_talks, dont_filter=True)

    def parse_talks(self, response):

        item = TedscraperItem()
        item['talk_title'] = response.xpath(self.elements['talk_title']).extract_first()
        item['talk_link'] = response.url
        item['talk_topics'] = response.xpath(self.elements['talk_topics']).extract()
        item['upload_date'] = response.xpath(self.elements['upload_date']).extract_first()
        item['langs'] = response.xpath(self.elements['langs']).extract()
        item['langs'].remove('x-default')

        item['transcripts'] = {}
        item['times'] = {}
        for lang in item['langs']:

            transcript_abs_url = '{}/transcript?language={}'.format(response.url, lang)
            transcript_url = response.urljoin(transcript_abs_url)
            with urlopen(transcript_url) as res:
                html = res.read()

            soup = BeautifulSoup(html, 'lxml')
            transcripts = []
            times = []
            for div_Grid__cell in self.parse_transcripts(soup):
                p = div_Grid__cell.find('p')
                if p is not None:
                    transcripts.append(p.get_text())
                else:
                    times.append(div_Grid__cell.get_text())

            item['transcripts'][lang] = transcripts[:-1]
            item['times'][lang] = times

        yield item

    def parse_transcripts(self, soup):
        return soup.find_all('div', {'class': 'Grid__cell'})
