# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin

import time


class TEDScraper:

    def __init__(self, url, lang="en"):
        """
        :param str url:
        :param str lang="en":
        """
        self.base_url = url
        self.target_url = self.base_url + "?language=" + lang

        self.all_talk_links = []
        self.all_talk_topics = []
        self.all_talk_texts = []

    def _make_soup(self, url):
        """
        URLからBeautifulSoupのインスタンスを返す。
        :param str url:
        :rtype: bs4.BeautifulSoup
        """
        with urlopen(url) as res:
            html = res.read()

        return BeautifulSoup(html, "lxml")

    def get_talk_links(self, soup):
        """
        現在のトーク一覧から各トークへのリンクを取得し、
        リンクをアドレスにアドレスを格納して返す。
        :param bs4.BeautifulSoup soup:
        :rtype: List
        """
        talk_links = soup.find_all("div", {"class": "talk-link"})
        talk_addresses = [self._find_talk_a(tl) for tl in talk_links]
        talk_addresses = [urljoin(self.base_url, ta) for ta in talk_addresses]

        return talk_addresses

    def get_all_talk_links(self):
        """
        各トークへのリンクをすべて取得する。
        """
        page_counter = 1
        while True:
            soup = self._make_soup(self.target_url)
            talk_links = self.get_talk_links(soup)
            self.all_talk_links.append(talk_links)
            next_link = self.get_next_talk_list_a(soup)

            if next_link is None:
                break

            page_counter += 1
            print("Now page: %d\n%s" % (page_counter, next_link))

            self.target_url = next_link
            time.sleep(2)

    def get_next_talk_list_a(self, soup):
        """
        次のトーク一覧へのリンクを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        pagination_div = soup.find("div", {"class": "pagination"})
        next_link_a = pagination_div.find("a", {"class", "pagination__next"})

        if next_link_a is None:
            return None

        next_link = next_link_a.attrs['href']
        next_link = urljoin(self.base_url, next_link)

        # print("next page url: %s" % next_link)

        return next_link

    def get_talk_topics(self, soup):
        """
        ターゲットとなっているトークのトピックのリストを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: List
        """

        talk_topics_items = self._find_talk_topics(soup)

        topic_list = []
        for tti in talk_topics_items:
            topic = tti.find("a")
            if topic is not None:
                topic = topic.get_text().replace("\n", "")
                print(topic)
                topic_list.append(topic)

        return topic_list

    def get_all_talk_topics(self):
        """
        すべてのトークのトピックのリストを返す
        """

        for all_talk_link in self.all_talk_links:
            for atl in all_talk_link:

                print("Target URL: %s" % atl)
                soup = self._make_soup(atl)

    def _find_talk_a(self, soup):
        """
        トークへのリンクアドレスを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        return soup.find("h4", {"class": "h9"}).find("a").attrs['href']

    def _find_talk_topics(self, soup):
        """
        トークのトピックのアイテムを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: bs4.element.ResultSet
        """
        talk_topics_div = soup.find("div", {"class", "talk-tipics"})
        return talk_topics_div.find_all("li", {"class": "talk_topics__item"})


if __name__ == '__main__':

    base_url = "https://www.ted.com/talks"

    ts = TEDScraper(base_url)
    ts.get_all_talk_links()
