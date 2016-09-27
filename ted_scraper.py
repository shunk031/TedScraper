# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin

import time
import re
import datetime
import json


class TEDScraper:

    BASE_URL = "https://www.ted.com/talks"
    LANG_URL = "https://www.ted.com/participate/translate/our-languages"

    def __init__(self, lang="en"):
        """
        :param str url:
        :param str lang="en":
        """
        self.lang = lang
        self.target_url = TEDScraper.BASE_URL + "?language=" + lang

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

            # print("[DEBUG] get_language lang type: %-25s symbol: %-5s %s" %
            #       (lang_type, lang_symbol, lang_talks))

            lang_info.append(
                {"lang_type": lang_type, "lang_symbol": lang_symbol, "lang_talks": lang_talks})

        return lang_info

    def get_talk_titles(self, soup):
        """
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """
        talk_titles = soup.find_all("div", {"class": "talk-link"})
        talk_titles = [self._find_talk_title(tt) for tt in talk_titles]
        return talk_titles

    def get_all_talk_titles(self, all_talk_links):
        """
        すべてのトークのタイトルのリストを返す。
        :param list all_talk_links:
        :rtype: list
        """
        all_talk_titles = []
        for all_talk_link in all_talk_links:
            for atl in all_talk_link:
                print("[DEBUG] get_all_talk_titles()\nTarget URL: %s" % atl)
                soup = TEDScraper.make_soup(atl)
                title_list = self.get_talk_titles(soup)

                all_talk_titles.append(title_list)
                time.sleep(1)

        return all_talk_titles

    def get_talk_posted_date(self, soup):
        """
        トークが投稿された年月のリストを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """

        posted_dates = soup.find_all("div", {"class": "talk-link"})
        posted_dates = [self._find_talk_posted_date(
            tpd) for tpd in posted_dates]
        posted_dates = [self._convert_date2str(tpd) for tpd in posted_dates]

        return posted_dates

    def get_talk_links(self, soup):
        """
        現在のトーク一覧から各トークへのリンクを取得し、
        リンクをアドレスにアドレスを格納して返す。
        :param bs4.BeautifulSoup soup:
        :rtype: List
        """
        talk_links = soup.find_all("div", {"class": "talk-link"})
        talk_addresses = [self._find_talk_a(tl) for tl in talk_links]
        talk_addresses = [urljoin(TEDScraper.BASE_URL, ta)
                          for ta in talk_addresses]

        return talk_addresses

    def get_all_talk_links(self):
        """
        各トークへのリンクをすべて取得する。
        :rtype: list
        """
        all_talk_links = []
        page_counter = 1
        while True:
            soup = TEDScraper.make_soup(self.target_url)
            talk_links = self.get_talk_links(soup)
            all_talk_links.append(talk_links)
            next_link = self.get_next_talk_list_a(soup)

            # DEBUG
            # if next_link is None:
            #     break
            if next_link:
                break

            page_counter += 1
            print("Now page: %d\n%s" % (page_counter, next_link))

            self.target_url = next_link
            time.sleep(1)

        return all_talk_links

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
        next_link = urljoin(TEDScraper.BASE_URL, next_link)

        # print("next page url: %s" % next_link)

        return next_link

    def get_talk_topics(self, soup):
        """
        ターゲットとなっているトークのトピックのリストを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: list
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

    def get_all_talk_topics(self, all_talk_links):
        """
        すべてのトークのトピックのリストを返す
        :param list all_talk_links:
        :rtype: list
        """
        all_talk_topics = []
        for all_talk_link in all_talk_links:
            for atl in all_talk_link:
                print("[DEBUG] get_all_talk_topics()\nTarget URL: %s" % atl)
                soup = TEDScraper.make_soup(atl)
                topic_list = self.get_talk_topics(soup)

                # print("[DEBUG] get_all_talk_topics()\nTopic List: %s" %
                #       topic_list)

                all_talk_topics.append(topic_list)
                time.sleep(1)

        return all_talk_topics

    def get_talk_transcript_time(self, soup):
        pass

    def get_all_talk_transcript_time(self, all_talk_links):
        pass

    def get_talk_transcrpit(self, soup):
        """
        ターゲットとなっているトークのTranscriptを取得する。
        :param bs4.BeautifulSoup soup:
        :rtype: list
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

    def get_all_talk_transcripts(self, all_talk_links):
        """
        すべてのトークのTranscriptを取得する。
        ;param list all_talk_links:
        ;rtype: list
        """
        all_talk_transcripts = []
        for all_talk_link in all_talk_links:
            for atl in all_talk_link:
                target = self._get_transcript_url(atl)
                # print("[DEBUG] get_all_talk_transcripts()\nTarget URL: %s" % target)

                soup = TEDScraper.make_soup(target)
                paragraph_list = self.get_talk_transcrpit(soup)

                # print("[DEBUG] get_all_talk_transcripts()\nPara List: %s\n" %
                #       paragraph_list)

                all_talk_transcripts.append(paragraph_list)
                time.sleep(1)

        return all_talk_transcripts

    def dump_talk_info(self, url):
        """
        URLから各トークのトーク情報をJSONファイルとして出力する。
        :param str url:
        """
        soup = TEDScraper.make_soup(url)

        print("Now get scrape date ...")
        update_date = self._get_scrape_date()

        print("Now get talk posted date ...")
        talk_date = self.get_talk_posted_date(soup)

        print("Now get talk titles ...")
        talk_titles = self.get_talk_titles(soup)

        print("Now get talk links ...")
        talk_links = self.get_talk_links(soup)

        print("Now get talk language ...")
        talk_lang = self.lang

        talk_topics = []
        talk_transcript = []
        for tl in talk_links:
            s = TEDScraper.make_soup(tl)
            talk_topics.append(self.get_talk_topics(s))
            transcript_url = self._get_transcript_url(tl)
            s = TEDScraper.make_soup(transcript_url)
            talk_transcript.append(self.get_talk_transcrpit(s))

        # dump talk info
        print("Now dump talk info ...")
        for date, title, link, topics, transcript in zip(talk_date, talk_titles, talk_links, talk_topics, talk_transcript):
            talk_info = {
                "posted_date": date,
                "update_date": update_date,
                "talk_title": title,
                "talk_link": link,
                "talk_lang": talk_lang,
                "talk_topics": topics,
                "talk_transcript": transcript
            }

            with open("./dump_files/talk_info_" + title + ".json", "w") as f:
                json.dump(talk_info, f, indent=2)

    def _find_talk_posted_date(self, soup):
        """
        トークが投稿された年月のリストを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        return soup.find("div", {"class": "meta"}).find("span", {"class": "meta__val"}).get_text().strip()

    def _find_talk_a(self, soup):
        """
        トークへのリンクアドレスを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        return soup.find("h4", {"class": "h9"}).find("a").attrs['href']

    def _find_talk_title(self, soup):
        """
        トークのタイトルを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: str
        """
        return soup.find("h4", {"class": "h9"}).find("a").get_text().strip()

    def _find_talk_topics(self, soup):
        """
        トークのトピックのアイテムタグ返す。
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
        Transcriptのパラグラフテキストタグを返す。
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

    def _get_scrape_date(self):
        """
        スクレイピングを実行した日付を返す。
        :rtype: datetime.date
        """
        today = datetime.date.today()
        return today.strftime('%Y-%m-%d')

    def _convert_date2str(self, date):
        """
        :param str date:
        :rtype: str
        """
        tdatetime = datetime.datetime.strptime(date, "%b %Y")
        tdatetime = tdatetime.strftime("%Y-%m-%d")
        # print("[DEBUG] _convert_date2str() %s" % tdatetime)
        return tdatetime

if __name__ == '__main__':

    base_url = "https://www.ted.com/talks"

    ts = TEDScraper(base_url)

    ts.get_all_talk_links()
    ts.get_all_talk_topics()
    ts.get_all_talk_transcripts()
