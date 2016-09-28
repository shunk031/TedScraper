# -*- coding: utf-8 -*-

from ted_scraper import TEDScraper
from pprint import pprint
import json
import time


if __name__ == '__main__':

    ts = TEDScraper()
    soup = TEDScraper.make_soup(TEDScraper.BASE_URL)

    # [TEST] TEDScraper.get_languages
    # available_language = TEDScraper.get_languages()
    # print("%s\n" % available_language)

    # [TEST] TEDScraper#get_talk_titles
    # talk_titles = ts.get_talk_titles(soup)
    # print("%s\n" % talk_titles)

    # [TEST] TEDScraper#get_talk_posted_date
    # talk_posted_date = ts.get_talk_posted_date(soup)
    # print("%s\n" % talk_posted_date)

    # [TEST] TEDScraper#get_talk_links
    # talk_links = ts.get_talk_links(soup)
    # print("%s\n" % talk_links)

    # # [TEST] TEDScraper#get_all_talk_links
    # all_talk_links = ts.get_all_talk_links()

    # [TEST] TEDScraper#get_talk_topics
    # talk_topics = []
    # for talk_link in talk_links:
    #     t_soup = TEDScraper.make_soup(talk_link)
    #     talk_topics.append(ts.get_talk_topics(t_soup))
    # print("%s\n" % talk_topics)

    # [TEST] TEDScraper#get_transcript_time
    # transcript_time = []
    # for talk_link in talk_links:
    #     transcript_url = TEDScraper.get_transcript_url(talk_link)
    #     t_soup = TEDScraper.make_soup(transcript_url)
    #     transcript_time.append(ts.get_talk_transcript_time(t_soup))
    # print("%s\n" % transcript_time)

    # [TEST] TEDScraper#get_talk_transcript
    # transcript_text = []
    # for talk_link in talk_links:
    #     transcript_url = TEDScraper.get_transcript_url(talk_link)
    #     t_soup = TEDScraper.make_soup(transcript_url)
    #     transcript_text.append(ts.get_talk_transcrpit(t_soup))
    # print("%s\n" % transcript_text)

    # for t_times, t_texts in zip(transcript_time, transcript_text):
    #     for t_time, t_text in zip(t_times, t_texts):
    #         print("%-10s : %s" % (t_time, t_text))

    # [TEST] TEDScraper#get_all_language_transcript
    # print("Now url 1")
    # talk_url1 = "https://www.ted.com/talks/ken_robinson_says_schools_kill_creativity"
    # all_lang_transcript = ts.get_all_language_transcript(talk_url1, 1)
    # print(all_lang_transcript)

    # [TEST] TEDScraper#get_available_language
    # available_lang = ts.get_available_language(talk_url)
    # print(available_lang)

    # talk_url2 = "https://www.ted.com/talks/amy_cuddy_your_body_language_shapes_who_you_are"
    # talk_url3 = "https://www.ted.com/talks/simon_sinek_how_great_leaders_inspire_action"
    # talk_url4 = "https://www.ted.com/talks/brene_brown_on_vulnerability"
    # talk_url5 = "https://www.ted.com/talks/mary_roach_10_things_you_didn_t_know_about_orgasm"

    # print("Now url 2")
    # all_lang_transcript = ts.get_all_language_transcript(talk_url2, 2)
    # print("Now url 3")
    # all_lang_transcript = ts.get_all_language_transcript(talk_url3, 3)
    # print("Now url 4")
    # all_lang_transcript = ts.get_all_language_transcript(talk_url4, 4)
    # print("Now url 5")
    # all_lang_transcript = ts.get_all_language_transcript(talk_url5, 5)

    start = time.time()
    ts.dump_talk_info_al("https://www.ted.com/talks")
    stop = time.time()
    print("[ TEST ] processed time: %s" % (stop - start))
