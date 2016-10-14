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
        self.target_url = TEDScraper.BASE_URL  # ターゲットとなっているURL
        self.target_page_list = 0  # トーク一覧ページ数
        self.target_page_num = 0  # トークページ数
        self.target_talk = ""  # トークタイトル
        self.all_page_list = 0
        self.all_talk_page_num = 0  # すべてのトーク数
        self.start_time = 0
        self.end_time = 0
        self.all_processing_time = 0  # 実行時間

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

    def get_talk_titles(self, ta_soup):
        """
        トークのタイトルを取得する。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """
        talk_titles = ta_soup.find_all("div", {"class": "talk-link"})
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
                self.target_url = atl
                print("[DEBUG] get_all_talk_titles()\nTarget URL: %s" % atl)
                soup = TEDScraper.make_soup(atl)
                title_list = self.get_talk_titles(soup)

                all_talk_titles.append(title_list)
                # time.sleep(1)

        return all_talk_titles

    def get_talk_posted_date(self, ta_soup):
        """
        トークが投稿された年月のリストを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """
        posted_dates = ta_soup.find_all("div", {"class": "talk-link"})
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

    def get_talk_links(self, ta_soup):
        """
        現在のトーク一覧から各トークへのリンクを取得し、
        リンクをアドレスにアドレスを格納して返す。
        :param bs4.BeautifulSoup soup:
        :rtype: List
        """
        talk_links = ta_soup.find_all("div", {"class": "talk-link"})
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
        target_url = TEDScraper.BASE_URL

        while True:
            soup = TEDScraper.make_soup(target_url)
            talk_links = self.get_talk_links(soup)
            all_talk_links.append(talk_links)
            next_link = self.get_next_talk_list_a(soup)

            if next_link is None:
                break

            page_counter += 1
            print("[ FIND ] Now page: %d" % page_counter)
            print("         %s" % next_link)

            target_url = next_link
            # time.sleep(1)

        return all_talk_links

    def get_all_talk_page_list(self):
        """
        トーク一覧ページをすべて取得する。
        :rtype: list
        """
        target_url = TEDScraper.BASE_URL
        page_list = []

        page_counter = 1
        page_list.append(target_url)

        while True:
            # print("[DEBUG] target_url: %s" % target_url)
            ta_soup = TEDScraper.make_soup(target_url)
            next_link = self.get_next_talk_list_a(ta_soup)

            if next_link is None:
                break

            page_counter += 1
            print("[ FIND ] Now page: %d" % page_counter)
            print("         %s" % next_link)
            target_url = next_link
            page_list.append(next_link)

        return page_list

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

    def get_talk_topics(self, ta_soup):
        """
        ターゲットとなっているトークのトピックのリストを返す。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """

        talk_topics_items = self._find_talk_topics(ta_soup)
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
                self.target_url = atl
                print("[DEBUG] get_all_talk_topics()\nTarget URL: %s" % atl)
                ta_soup = TEDScraper.make_soup(atl)
                topic_list = self.get_talk_topics(ta_soup)

                # print("[DEBUG] get_all_talk_topics()\nTopic List: %s" %
                #       topic_list)

                all_talk_topics.append(topic_list)
                # time.sleep(1)

        return all_talk_topics

    def get_talk_transcript_time(self, tr_soup):
        """
        ターゲットとなっているトークのTranscript Timeを取得する。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """
        try:
            talk_transcript_para = self._find_transcript_para(tr_soup)

            time_list = []
            for ttp in talk_transcript_para:
                tt = self._find_transcript_time(ttp)
                transcript_time = self._format_string(tt).replace(" ", "")
                time_list.append(transcript_time)

            return time_list

        except AttributeError as e:
            print(
                "[DEBUG] in get_talk_transcript_time(): Raise AttributeError exception:")
            print("        %s" % e)
            time_list.apppend("no time data found.")
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
                tr_url = TEDScraper.get_transcript_url(atl, self.lang)
                self.target_url = tr_url
                tr_soup = TEDScraper.make_soup(tr_url)
                time_list = self.get_talk_transcript_time(tr_soup)

                all_talk_transcript_time.append(time_list)
                # time.sleep(1)

        return all_talk_transcript_time

    def get_talk_transcrpit(self, tr_soup):
        """
        ターゲットとなっているトークのTranscriptを取得する。
        :param bs4.BeautifulSoup soup:
        :rtype: list
        """
        talk_transcript_para = self._find_transcript_para(tr_soup)
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
                tr_url = TEDScraper.get_transcript_url(atl, self.lang)
                self.target_url = tr_url
                # print("[DEBUG] get_all_talk_transcripts()\nTarget URL: %s" % target)

                tr_soup = TEDScraper.make_soup(tr_url)
                paragraph_list = self.get_talk_transcrpit(tr_soup)

                # print("[DEBUG] get_all_talk_transcripts()\nPara List: %s\n" %
                #       paragraph_list)

                all_talk_transcripts.append(paragraph_list)
                # time.sleep(1)

        return all_talk_transcripts

    def get_all_language_transcript(self, ta_url):
        """
        ターゲットなるトークで利用できるすべての言語の
        Transcriptを取得する。
        :param str talk_url:
        :rtype: dict
        """
        t_dict = {}

        try:
            available_lang = self.get_available_language(ta_url)
        except AttributeError as e:
            print(
                "[DEBUG] in get_all_language_transcript(): Raise AttributeError exception:")
            print("        %s" % e)

            t_dict["none"] = "no transcript text found."
            return t_dict

        lang_num = len(available_lang)
        for i, al in enumerate(available_lang):
            tr_url = TEDScraper.get_transcript_url(ta_url, al)
            print(
                "                  [%3d/%3d] target language: %s" % (i + 1, lang_num, al))
            # print("[DEBUG] in get_all_language_transcript()")
            # print("[DEBUG] symbol: %-5s URL: %s\n" %
            #       (al, t_url))

            tr_soup = TEDScraper.make_soup(tr_url)
            if tr_soup is not None:
                t_dict[al] = self.get_talk_transcrpit(tr_soup)

                # [DEBUG] dump json file
                # with open("./dump_files/talk_info_al" + str(num) + ".json", "w") as f:
                #     json.dump(t_dict, f, indent=2)

        return t_dict

    def get_available_language(self, ta_url):
        """
        ターゲットとなるトークで利用できる言語を返す。
        :param str talk_url:
        :rtype: list
        """
        tr_url = TEDScraper.get_transcript_url(ta_url)
        tr_soup = TEDScraper.make_soup(tr_url)
        talk_transcript_language = self._find_transcript_language(tr_soup)

        available_lang = []
        for ttl in talk_transcript_language:
            available_lang.append(ttl.attrs["value"])

        return available_lang

    def dump_talk_info(self, ta_url, save_dir=None):
        """
        トーク一覧URLから各トークのトーク情報をJSONファイルとして出力する。
        :param str url:
        """
        # create save dir if not exist
        if save_dir is None:
            save_dir = "./dump_files"
            if not os.path.isdir("dump_files"):
                os.mkdir("dump_files")
                print("[ CREATE ] create default dump dir ...")
        else:
            save_dir = os.path.expanduser(save_dir)
            if not os.path.isdir(save_dir):
                print("[ CREATE ] create dump dir: %s" % save_dir)
                os.makedirs(save_dir)

        self.target_url = ta_url
        ta_soup = TEDScraper.make_soup(ta_url)

        print("[ GET ] get scrape date ...")
        update_date = self._get_scrape_date()
        print("[ GET ] get talk posted date ...")
        talk_date = self.get_talk_posted_date(ta_soup)
        print("[ GET ] get talk titles ...")
        talk_titles = self.get_talk_titles(ta_soup)
        print("[ GET ] get talk links ...")
        talk_links = self.get_talk_links(ta_soup)
        print("[ GET ] get talk language ...")
        talk_lang = self.lang

        talk_topics = []
        talk_transcript = []
        transcript_time = []

        talk_num = len(talk_links)
        self.all_page_list = talk_num

        print("[ GET ] get talk topics and transcripts ...")
        for i, tl in enumerate(talk_links):
            self.target_page_num = i + 1
            self.target_url = tl
            print("  [%d/%d] Target URL: %s" % (i + 1, talk_num, tl))
            ta_soup = TEDScraper.make_soup(tl)

            print("          [ GET ] get talk topics")
            talk_topics.append(self.get_talk_topics(ta_soup))

            print("          [ GET ] get talk transcript")

            tr_url = TEDScraper.get_transcript_url(tl, self.lang)
            self.target_url = tr_url
            print("          Target transcript URL: %s" % tr_url)
            tr_soup = TEDScraper.make_soup(tr_url)

            talk_transcript.append(self.get_talk_transcrpit(tr_soup))
            print("            [ GET ] get transcript time")
            transcript_time.append(self.get_talk_transcript_time(tr_soup))

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
                "transcript": transcript,
                "time": t_time
            }

            filename = os.path.join(save_dir, title + ".json")
            filename = self._format_filename(filename)

            print("         dump file: %s" % filename)
            with open(filename, "w") as f:
                json.dump(talk_info, f, indent=2)

    def dump_talk_info_al(self, ta_url, save_dir=None):
        """
        トーク一覧URLから投稿日、データ収集日、トークタイトル、トークへのリンク、
        トークのトピック、利用できる言語すべてのTranscriptをJSONファイルとして出力する。
        :param str talk_url:
        """
        # create save dir if not exist
        if save_dir is None:
            save_dir = "./dump_files"
            if not os.path.isdir("dump_files"):
                os.mkdir("dump_files")
                print("[ CREATE ] create default dump dir ...")
        else:
            save_dir = os.path.expanduser(save_dir)
            if not os.path.isdir(save_dir):
                print("[ CREATE ] create dump dir: %s" % save_dir)
                os.makedirs(save_dir)

        self.target_url = ta_url
        ta_soup = TEDScraper.make_soup(ta_url)

        print("[ GET ] get scrape date ...")
        update_date = self._get_scrape_date()
        print("[ GET ] get talk posted date ...")
        talk_date = self.get_talk_posted_date(ta_soup)
        print("[ GET ] get talk titles ...")
        talk_titles = self.get_talk_titles(ta_soup)
        print("[ GET ] get talk links ...")
        talk_links = self.get_talk_links(ta_soup)

        talk_topics = []
        talk_transcript = []
        transcript_time = []

        talk_num = len(talk_links)
        self.all_page_list = talk_num

        print("[ GET ] get talk topics and transcripts ...")
        for i, tl in enumerate(talk_links):
            self.target_page_num = i + 1
            self.target_url = tl
            print("  [%d/%d] Target URL: %s" % (i + 1, talk_num, tl))
            ta_soup = TEDScraper.make_soup(tl)

            print("          [ GET ] get talk topics")
            talk_topics.append(self.get_talk_topics(ta_soup))

            print("          [ GET ] get all language talk transcript")
            talk_transcript.append(self.get_all_language_transcript(tl))

            tr_url = TEDScraper.get_transcript_url(tl)
            self.target_url = tr_url
            print("          Target transcript URL: %s" % tr_url)
            tr_soup = TEDScraper.make_soup(tr_url)

            print("            [ GET ] get transcript time")
            transcript_time.append(self.get_talk_transcript_time(tr_soup))

        # dump talk info
        print("[ DUMP ] dump talk info ... ")
        for date, title, link, topics, transcript, t_time in zip(talk_date, talk_titles, talk_links, talk_topics, talk_transcript, transcript_time):

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

    def dump_all_talk_info_al(self, save_dir=None, page_list=None):
        """
        全トークについて、投稿日、データ収集日、トークタイトル、トークへのリンク、
        トークのトピック、利用できる言語すべてのTranscriptをJSONファイルとして出力する。
        :param list page_list:
        :param str save_dir:
        """
        try:
            if page_list is None:
                page_list = self.get_all_talk_page_list()

            page_num = len(page_list)
            self.all_talk_page_num = page_num

            for i, pl in enumerate(page_list):
                self.start_time = time.time()
                self.target_page_list = i + 1
                print("[ PROGRESS ] %d/%d page" % (i + 1, page_num))
                self.dump_talk_info_al(pl, save_dir)
                self.end_time = time.time()
                process_time = (self.end_time - self.start_time) / 60
                print("[ TIME ] %2.2f [min]" % process_time)
                self.all_processing_time += process_time
        except:
            self.end_time = time.time()
            process_time = (self.end_time - self.start_time) / 60
            self.all_processing_time += process_time

            import traceback
            traceback.print_exc()

            print("[DEBUG] Raise except:")
            print("[DEBUG] Target URL: %s" % self.target_url)

            print("[DEBUG] All progress:%2d/%2d" %
                  (self.target_page_list, self.all_talk_page_num))
            print("        Process page:%2d/%2d" %
                  (self.target_page_num, self.all_page_list))

            print("[DEBUG] Process time: %2.2f [min]" %
                  self.all_processing_time)

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

    def _find_transcript_language(self, tr_soup):

        return tr_soup.find("select", {"class": "talk-transcript__language"}).find_all("option")

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
