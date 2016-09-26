# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin

import time
import re


class TEDScraper:

    LANG_URL = "https://www.ted.com/participate/translate/our-languages"

    def __init__(self, url, lang="en"):
        """
        :param str url:
        :param str lang="en":
        """
        self.base_url = url
        self.lang = lang
        self.target_url = self.base_url + "?language=" + lang

        self.all_talk_topics = []
        self.all_talk_links = []
        self.all_talk_topics = []
        self.all_talk_transcripts = []

    @staticmethod
    def make_soup(url):
        """
        URLからBeautifulSoupのインスタンスを返す。
        :param str url:
        :rtype: bs4.BeautifulSoup
        """
        with urlopen(url) as res:
            html = res.read()

        return BeautifulSoup(html, "lxml")

    @staticmethod
    def get_languages():
        """
        取得できる言語とそのシンボル、トーク数を返す。
        :rtype dict
        """
        soup = TEDScraper.make_soup(TEDScraper.LANG_URL)
        lang_div = soup.find_all("div", {"class": "languages__list__language"})

        lang_info = []
        for ld in lang_div:
            lang_type = ld.find("a").get_text()
            lang_symbol = ld.find("a").attrs['href'].replace(
                "/talks?language=", "")
            lang_talks = ld.get_text().replace("\n", "").replace(lang_type, "")
            lang_talks = re.match("\d*", lang_talks)
            lang_talks = lang_talks.group()

            print("[DEBUG] get_language lang type: %-25s symbol: %-5s %s" %
                  (lang_type, lang_symbol, lang_talks))

            lang_info.append(
                {"lang_type": lang_type, "lang_symbol": lang_symbol, "lang_talks": lang_talks})

        return lang_info

    def get_talk_titles(self, soup):
        talk_titles = soup.find_all("div", {"class": "talk-link"})
        talk_titles = [self._get_talk_title(tt) for tt in talk_titles]

        return talk_titles

    def get_all_talk_titles(self):
        pass

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
            soup = TEDScraper.make_soup(self.target_url)
            talk_links = self.get_talk_links(soup)
            self.all_talk_links.append(talk_links)
            next_link = self.get_next_talk_list_a(soup)

            # DEBUG
            # if next_link is None:
            #     break
            if next_link:
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
        # print("[DEBUG] Now TEDScraper get_talk_topics() talk_topics_items = %s" %
        #       talk_topics_items)

        topic_list = []
        for tti in talk_topics_items:
            topic = tti.find("a")

            if topic is not None:
                topic = topic.get_text().replace("\n", "")
                # print("[DEBUG] Now TEDScraper get_talk_topics() topic = %s" % topic)
                topic_list.append(topic)

        return topic_list

    def get_all_talk_topics(self):
        """
        すべてのトークのトピックのリストを返す
        """

        for all_talk_link in self.all_talk_links:
            for atl in all_talk_link:
                print("[DEBUG] get_all_talk_topics()\nTarget URL: %s" % atl)
                soup = TEDScraper.make_soup(atl)
                topic_list = self.get_talk_topics(soup)

                print("[DEBUG] get_all_talk_topics()\nTopic List: %s" %
                      topic_list)

                self.all_talk_topics.append(topic_list)
                time.sleep(2)

    def get_talk_transcrpit(self, soup):
        """
        ターゲットとなっているトークのTranscriptを取得する。
        :param bs4.BeautifulSoup soup:
        :rtype: List
        """
        talk_transcript_para = self._find_transcript_para(soup)
        # print("[DEBUG] get_talk_transcript()\n Transcript Para: %s" %
        #       talk_transcript_para)

        paragraph_list = []
        for ttp in talk_transcript_para:
            tt = self._find_transcript_text(ttp)
            transcript_text = self._format_string(tt)
            # print("[DEBUG] get_talk_transcript()\n Transcript Text: %s" %
            #       transcript_text)
            paragraph_list.append(transcript_text)

        return paragraph_list

    def get_all_talk_transcripts(self):
        """
        すべてのトークのTranscriptを取得する。
        """
        for all_talk_link in self.all_talk_links:
            for atl in all_talk_link:
                target = self._get_transcript_url(atl)
                print("[DEBUG] get_all_talk_transcripts()\nTarget URL: %s" % target)

                soup = TEDScraper.make_soup(target)
                paragraph_list = self.get_talk_transcrpit(soup)

                print("[DEBUG] get_all_talk_transcripts()\nPara List: %s\n" %
                      paragraph_list)

                self.all_talk_transcripts.append(paragraph_list)
                time.sleep(2)

    def _find_talk_a(self, soup):
        """
        トークへのリンクアドレスを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        return soup.find("h4", {"class": "h9"}).find("a").attrs['href']

    def _get_talk_title(self, soup):
        """
        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        return soup.find("h4", {"class": "h9"}).find("a").get_text()

    def _find_talk_topics(self, soup):
        """
        トークのトピックのアイテムを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: bs4.element.ResultSet
        """
        talk_topics_div = soup.find("div", {"class", "talk-topics"})
        return talk_topics_div.find_all("li", {"class": "talk-topics__item"})

    def _find_transcript_para(self, soup):
        """
        Transcriptのパラグラフタグを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: bs4.element.ResultSet
        """
        return soup.find_all("p", {"class": "talk-transcript__para"})

    def _find_transcript_text(self, soup):
        """
        Transcriptのパラグラフテキストを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: bs4.element.ResultSet
        """
        return soup.find("span", {"class": "talk-transcript__para__text"})

    def _format_string(self, s):
        """
        文字列をを整形して返す。
        :param str s:
        :rtype: str
        """
        return s.get_text().replace("\n", "")

    def _get_transcript_url(self, s):
        """
        トークへのリンクからトークのTranscriptへのリンクを生成する。
        :param str s:
        :rtype: str
        """
        r1 = "?language=" + self.lang
        r2 = "/transcript?language=" + self.lang
        transcript_url = s.replace(r1, r2)

        return transcript_url


if __name__ == '__main__':

    base_url = "https://www.ted.com/talks"

    ts = TEDScraper(base_url)

    ts.get_all_talk_links()
    ts.get_all_talk_topics()
    ts.get_all_talk_transcripts()
