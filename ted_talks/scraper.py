# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError

import time
import re
import datetime
import json
import os


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

    @staticmethod
    def make_soup(url):
        """
        URLからBeautifulSoupのインスタンスを返す。
        :param str url:
        :rtype: bs4.BeautifulSoup
        """
        try:
            with urlopen(url) as res:
                # print("[DEBUG] in make_soup() : Found: %s" % url)
                html = res.read()

        except HTTPError as e:
            print("[DEBUG] in make_soup() : Raise HTTPError exception:")
            print("[DEBUG] URL: %s %s" % (url, e))
            return None

        return BeautifulSoup(html, "lxml")

    @staticmethod
    def get_languages():
        """
        取得できる言語とそのシンボル、トーク数を返す。
        :rtype list
        """
        soup = TEDScraper.make_soup(TEDScraper.LANG_URL)
        lang_div = soup.find_all("div", {"class": "languages__list__language"})

        lang_info = []
        for ld in lang_div:
            lang_type = ld.find("a").get_text()
            lang_symbol = ld.find("a").attrs['href'].replace(
                "/talks?language=", "")
            lang_talks = ld.get_text().strip().replace(lang_type, "")
            lang_talks = re.match("\d*", lang_talks)
            lang_talks = lang_talks.group()

            # print("[DEBUG] get_language lang type: %-25s symbol: %-5s %s" %
            #       (lang_type, lang_symbol, lang_talks))

            lang_info.append(
                {"lang_type": lang_type, "lang_symbol": lang_symbol, "lang_talks": lang_talks})

        return lang_info

    @staticmethod
    def get_transcript_url(s, lang="en"):
        """
        トークへのリンクからトークのTranscriptへのリンクを生成する。
        :param str s:
        :rtype: str
        """
        r1 = "?language=" + lang
        r2 = "/transcript?language=" + lang

        is_match = re.match(".*(\?language=).*", s)
        if is_match:
            t_url = s.replace(r1, r2)
        else:
            t_url = s + r2

        return t_url

    def get_talk_titles(self, soup):
        """
        トークのタイトルを取得する。
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
                # time.sleep(1)

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

    def get_all_talk_posted_date(self, all_talk_links):
        """
        すべてのトークの投稿日のリストを返す。
        :param list all_talk_links:
        :rtype: list
        """
        all_talk_posted_date = []
        for all_talk_link in all_talk_links:
            for atl in all_talk_links:
                soup = TEDScraper.make_soup(atl)
                posted_date = self.get_talk_posted_date(soup)
                all_talk_posted_date.append(posted_date)
                # time.sleep(1)

        return all_talk_posted_date

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
        page_list = []
        while True:
            soup = TEDScraper.make_soup(self.target_url)
            talk_links = self.get_talk_links(soup)
            all_talk_links.append(talk_links)
            next_link = self.get_next_talk_list_a(soup)

            if next_link is None:
                break

            page_counter += 1
            print("Now page: %d\n%s" % (page_counter, next_link))

            self.target_url = next_link
            page_list.append(next_link)
            # time.sleep(1)

        return all_talk_links, page_list

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

    def get_talk_topics(self, t_soup):
        """
        ターゲットとなっているトークのトピックのリストを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """

        talk_topics_items = self._find_talk_topics(t_soup)
        # print("[DEBUG] Now TEDScraper get_talk_topics() talk_topics_items = %s" %
        #       talk_topics_items)

        topic_list = []
        for tti in talk_topics_items:
            topic = tti.find("a")

            if topic is not None:
                topic = topic.get_text().strip()
                # print("[DEBUG] Now TEDScraper get_talk_topics() topic = %s" % topic)
                topic_list.append(topic)

        return topic_list

    def get_all_talk_topics(self, all_talk_links):
        """
        すべてのトークのトピックのリストを返す。
        :param list all_talk_links:
        :rtype: list
        """
        all_talk_topics = []
        for all_talk_link in all_talk_links:
            for atl in all_talk_link:
                print("[DEBUG] get_all_talk_topics()\nTarget URL: %s" % atl)
                t_soup = TEDScraper.make_soup(atl)
                topic_list = self.get_talk_topics(t_soup)

                # print("[DEBUG] get_all_talk_topics()\nTopic List: %s" %
                #       topic_list)

                all_talk_topics.append(topic_list)
                # time.sleep(1)

        return all_talk_topics

    def get_talk_transcript_time(self, t_soup):
        """
        ターゲットとなっているトークのTranscript Timeを取得する。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """
        talk_transcript_para = self._find_transcript_para(t_soup)

        time_list = []
        for ttp in talk_transcript_para:
            tt = self._find_transcript_time(ttp)
            transcript_time = self._format_string(tt).replace(" ", "")
            time_list.append(transcript_time)

        return time_list

    def get_all_talk_transcript_time(self, all_talk_links):
        """
        すべてのトークのTranscript Timeを取得する。
        :param list all_talk_links:
        :rtype: list
        """

        all_talk_transcript_time = []
        for all_talk_link in all_talk_links:
            for atl in all_talk_link:
                t_url = TEDScraper.get_transcript_url(atl, self.lang)

                t_soup = TEDScraper.make_soup(t_url)
                time_list = self.get_talk_transcript_time(t_soup)

                all_talk_transcript_time.append(time_list)
                # time.sleep(1)

        return all_talk_transcript_time

    def get_talk_transcrpit(self, t_soup):
        """
        ターゲットとなっているトークのTranscriptを取得する。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """
        talk_transcript_para = self._find_transcript_para(t_soup)
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
                t_url = TEDScraper.get_transcript_url(atl, self.lang)
                # print("[DEBUG] get_all_talk_transcripts()\nTarget URL: %s" % target)

                soup = TEDScraper.make_soup(t_url)
                paragraph_list = self.get_talk_transcrpit(soup)

                # print("[DEBUG] get_all_talk_transcripts()\nPara List: %s\n" %
                #       paragraph_list)

                all_talk_transcripts.append(paragraph_list)
                # time.sleep(1)

        return all_talk_transcripts

    def get_all_language_transcript(self, talk_url):
        """
        ターゲットなるトークで利用できるすべての言語の
        Transcriptを取得する。
        :param str talk_url:
        :rtype: dict
        """
        t_dict = {}
        available_lang = self.get_available_language(talk_url)

        for al in available_lang:
            t_url = TEDScraper.get_transcript_url(talk_url, al)

            # print("[DEBUG] in get_all_language_transcript()")
            # print("[DEBUG] symbol: %-5s URL: %s\n" %
            #       (al, t_url))

            t_soup = TEDScraper.make_soup(t_url)
            if t_soup is not None:
                t_dict[al] = self.get_talk_transcrpit(t_soup)

                # [DEBUG] dump json file
                # with open("./dump_files/talk_info_al" + str(num) + ".json", "w") as f:
                #     json.dump(t_dict, f, indent=2)

        return t_dict

    def get_available_language(self, talk_url):
        """
        ターゲットとなるトークで利用できる言語を返す。
        :param str talk_url:
        :rtype: list
        """
        t_url = TEDScraper.get_transcript_url(talk_url)
        soup = TEDScraper.make_soup(t_url)
        talk_transcript_language = soup.find(
            "select", {"class": "talk-transcript__language"}).find_all("option")

        available_lang = []
        for ttl in talk_transcript_language:
            available_lang.append(ttl.attrs["value"])

        return available_lang

    def dump_talk_info(self, talk_url, save_dir):
        """
        トーク一覧URLから各トークのトーク情報をJSONファイルとして出力する。
        :param str url:
        """
        soup = TEDScraper.make_soup(talk_url)

        print("[ GET ] get scrape date ...")
        update_date = self._get_scrape_date()
        print("[ GET ] get talk posted date ...")
        talk_date = self.get_talk_posted_date(soup)
        print("[ GET ] get talk titles ...")
        talk_titles = self.get_talk_titles(soup)
        print("[ GET ] get talk links ...")
        talk_links = self.get_talk_links(soup)
        print("[ GET ] get talk language ...")
        talk_lang = self.lang

        talk_topics = []
        talk_transcript = []
        transcript_time = []
        talk_num = len(talk_links)
        print("[ GET ] get talk topics and transcripts ...")
        for i, tl in enumerate(talk_links):
            print("  [%d/%d] Target URL: %s" % (i + 1, talk_num, tl))
            soup = TEDScraper.make_soup(tl)
            print("          [ GET ] get talk topics")
            talk_topics.append(self.get_talk_topics(soup))
            print("          [ GET ] get talk transcript")
            t_url = TEDScraper.get_transcript_url(tl, self.lang)
            print("          Target transcript URL: %s" % t_url)
            t_soup = TEDScraper.make_soup(t_url)
            talk_transcript.append(self.get_talk_transcrpit(t_soup))
            print("            [ GET ] get transcript time")
            transcript_time.append(self.get_talk_transcript_time(t_soup))

        # create save dir if not exist
        save_dir = os.path.expanduser(save_dir)
        if not os.path.isdir(save_dir):
            print("[ CREATE ] create dump dir: %s" % save_dir)
            os.mkdir(save_dir)

        # dump talk info
        print("[ DUMP ] dump talk info ...")
        for date, title, link, topics, transcript, t_time in zip(talk_date, talk_titles, talk_links, talk_topics, talk_transcript, transcript_time):
            talk_info = {
                "posted_date": date,
                "update_date": update_date,
                "talk_title": title,
                "talk_link": link,
                "talk_lang": talk_lang,
                "talk_topics": topics,
                "talk_transcript": transcript,
                "transcript_time": t_time
            }

            filename = os.path.join(save_dir, title + ".json")
            filename = self._format_filename(filename)
            print("         dump file: %s" % filename)
            with open(filename, "w") as f:
                json.dump(talk_info, f, indent=2)

    def dump_talk_info_al(self, talk_url, save_dir):
        """
        トーク一覧URLから投稿日、データ収集日、トークタイトル、トークへのリンク、
        トークのトピック、利用できる言語すべてのTranscriptをJSONファイルとして出力する。
        :param str talk_url:
        """
        soup = TEDScraper.make_soup(talk_url)

        print("[ GET ] get scrape date ...")
        update_date = self._get_scrape_date()
        print("[ GET ] get talk posted date ...")
        talk_date = self.get_talk_posted_date(soup)
        print("[ GET ] get talk titles ...")
        talk_titles = self.get_talk_titles(soup)
        print("[ GET ] get talk links ...")
        talk_links = self.get_talk_links(soup)

        talk_topics = []
        talk_transcript = []
        transcript_time = []
        talk_num = len(talk_links)
        print("[ GET ] get talk topics and transcripts ...")
        for i, tl in enumerate(talk_links):
            print("  [%d/%d] Target URL: %s" % (i + 1, talk_num, tl))
            soup = TEDScraper.make_soup(tl)
            print("          [ GET ] get talk topics")
            talk_topics.append(self.get_talk_topics(soup))
            print("          [ GET ] get all language talk transcript")
            talk_transcript.append(self.get_all_language_transcript(tl))
            t_url = TEDScraper.get_transcript_url(tl)
            print("          Target transcript URL: %s" % t_url)
            t_soup = TEDScraper.make_soup(t_url)
            print("            [ GET ] get transcript time")
            transcript_time.append(self.get_talk_transcript_time(t_soup))

        # create save dir if not exist
        save_dir = os.path.expanduser(save_dir)
        if not os.path.isdir(save_dir):
            print("[ CREATE ] create dump dir: %s" % save_dir)
            os.mkdir(save_dir)

        # dump talk info
        print("[ DUMP ] dump talk info ... ")
        for date, title, link, topics, transcript, t_time in zip(talk_date, talk_titles, talk_links, talk_topics, talk_transcript, transcript_time):
            # print("         Title: %s, Posted Date: %s, Update Date: %s" %
            #       (title, update_date, date))
            # print("         Link Address: %s" % link)
            talk_info = {
                "posted_date": date,
                "update_date": update_date,
                "talk_title": title,
                "talk_link": link,
                "talk_topics": topics,
                "transcript": transcript,
                "time": t_time
            }

            filename = os.path.join(save_dir, "al-" + title + ".json")
            filename = self._format_filename(filename)
            print("         dump file: %s" % filename)
            with open(filename, "w") as f:
                json.dump(talk_info, f, indent=2)

    # TODO : save_dir
    def dump_all_talk_info_al(self, all_talk_links):

        for all_talk_link in all_talk_links:
            for atl in all_talk_link:
                # self.dump_talk_info_al(atl, save_dir)
                self.dump_talk_info_al(
                    atl, "~/Programing/Python/ted-scraper-dev/02/ted-scraper/dump_files")

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

    def _find_transcript_time(self, soup):
        """
        Transciprt timeのタグを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: bs4.element.ResultSet
        """
        return soup.find("data", {"class": "talk-transcript__para__time"})

    def _format_string(self, s):
        """
        文字列をを整形して返す。
        :param str s:
        :rtype: str
        """
        return s.get_text().replace("\n", "")

    def _format_filename(self, s):
        """
        ファイル名のスペースをアンダーバーに変換する。
        :param str s:
        :rtype: str
        """
        return s.replace(" ", "_")

    def _get_scrape_date(self):
        """
        スクレイピングを実行した日付を返す。
        :rtype: datetime.date
        """
        today = datetime.date.today()
        return today.strftime('%Y-%m-%d')

    def _convert_date2str(self, date):
        """
        今日の年月日をdatetime型で読めるような
        文字列フォーマットに変換する。
        :param str date:
        :rtype: str
        """
        tdatetime = datetime.datetime.strptime(date, "%b %Y")
        tdatetime = tdatetime.strftime("%Y-%m-%d")
        # print("[DEBUG] _convert_date2str() %s" % tdatetime)
        return tdatetime
