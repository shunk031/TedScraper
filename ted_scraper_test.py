# -*- coding: utf-8 -*-

import unittest
from ted_scraper import TEDScraper


class TEDScraperTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.ts = TEDScraper()

        soup = TEDScraper.make_soup(TEDScraper.BASE_URL)
        cls.soup = soup

    def test_make_soup(self):
        """
        TERScraper.BASE_URLを用いてsoupを生成した時にNoneではない場合True
        """
        self.assertIsNotNone(TEDScraperTest.soup)

    def test_get_language(self):
        """
        TEDScraper.get_languagesから帰ってくる結果の長さが0でない場合True
        """
        available_language = TEDScraper.get_languages()
        self.assertIsNot(len(available_language), 0)

    def test_get_talk_titles(self):
        talk_titles = TEDScraperTest.ts.get_talk_titles(TEDScraperTest.soup)
        self.assertIsNot(len(talk_titles), 0)

    def test_get_talk_posted_date(self):
        talk_posted_date = TEDScraperTest.ts.get_talk_posted_date(
            TEDScraperTest.soup)
        self.assertIsNot(len(talk_posted_date), 0)

    def test_get_talk_links(self):
        talk_links = TEDScraperTest.ts.get_talk_links(TEDScraperTest.soup)
        self.assertIsNot(len(talk_links), 0)

    def test_get_talk_topics(self):
        talk_links = TEDScraperTest.ts.get_talk_links(TEDScraperTest.soup)

        talk_topics = []
        for talk_link in talk_links:
            t_soup = TEDScraper.make_soup(talk_link)
            talk_topics.append(TEDScraperTest.ts.get_talk_topics(t_soup))

        for tt in talk_topics:
            if len(tt) == 0:
                self.assertFalse(len(tt) == 0)
                break

    def test_get_transcript_time(self):
        talk_links = TEDScraperTest.ts.get_talk_links(TEDScraperTest.soup)

        transcript_time = []
        for talk_link in talk_links:
            t_soup = TEDScraper.make_soup(talk_link)
            transcript_time.append(TEDScraperTest.ts.get_talk_topics(t_soup))

        for tt in transcript_time:
            if len(tt) == 0:
                self.assertFalse(len(tt) == 0)
                break

    def test_get_talk_transcript(self):
        talk_links = TEDScraperTest.ts.get_talk_links(TEDScraperTest.soup)

        transcript_text = []
        for talk_link in talk_links:
            t_url = TEDScraper.get_transcript_url(talk_link)
            t_soup = TEDScraper.make_soup(t_url)
            transcript_text.append(
                TEDScraperTest.ts.get_talk_transcrpit(t_soup))

        for tt in transcript_text:
            if len(tt) == 0:
                self.assertFalse(len(tt) == 0)
                break

    def test_get_all_language_transcript(self):
        test_talk_url = "https://www.ted.com/talks/ken_robinson_says_schools_kill_creativity"
        all_lang_transcript = TEDScraperTest.ts.get_all_language_transcript(
            test_talk_url)
        self.assertIsNot(len(all_lang_transcript), 0)

    def test_get_available_language(self):
        test_talk_url = "https://www.ted.com/talks/ken_robinson_says_schools_kill_creativity"
        available_lang = TEDScraperTest.ts.get_available_language(
            test_talk_url)

        self.assertIsNot(len(available_lang), 0)
