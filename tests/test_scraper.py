# -*- coding: utf-8 -*-

from ted_talks.scraper import TEDScraper

import unittest
import os
import json


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

    def test_get_all_talk_page_list(self):
        page_list = TEDScraperTest.ts.get_all_talk_page_list()
        self.assertIsNot(len(page_list), 0)

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

    def test_dump_talk_info(self):
        run_path = os.path.abspath(os.path.dirname("__file__"))
        save_dir = os.path.join(run_path, "dump_files")

        TEDScraperTest.ts.dump_talk_info("https://www.ted.com/talks", save_dir)

        dir_list = os.listdir(save_dir)
        for dl in dir_list:
            with open(os.path.join(save_dir, dl), 'r') as f:
                data = json.load(f)

                for v in data.values():
                    self.assertIsNot(len(v), 0)

    def test_dump_talk_info_al(self):
        run_path = os.path.abspath(os.path.dirname("__file__"))
        save_dir = os.path.join(run_path, "dump_files")

        TEDScraperTest.ts.dump_talk_info_al(
            "https://www.ted.com/talks", save_dir)

        dir_list = os.listdir(save_dir)
        for dl in dir_list:
            with open(os.path.join(save_dir, dl), 'r') as f:
                data = json.load(f)

                for v in data.values():
                    self.assertIsNot(len(v), 0)

    def test_specific_url(self):
        specific_url = [
            "https://www.ted.com/talks/how_much_does_a_video_weigh"
        ]

        run_path = os.path.abspath(os.path.dirname("__file__"))
        save_dir = os.path.join(run_path, "dump_files")

        for su in specific_url:
            print("Target URL: %s" % su)
            TEDScraperTest.ts.dump_talk_info_al(su, save_dir)

        dir_list = os.listdir(save_dir)
        print(dir_list)
        for dl in dir_list:
            print("filename: %s" % os.path.join(save_dir, dl))
            with open(os.path.join(save_dir, dl), 'r') as f:
                data = json.load(f)

                for v in data.values():
                    self.assertIsNot(len(v), 0)

if __name__ == '__main__':
    unittest.main()
