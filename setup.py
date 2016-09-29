# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='ted-scraper',
    version='',
    description='Scraper for TED Talks in Python. Get talk title, transcript, topics and so on.',
    author='Shunsuke KITADA',
    url='https://github.com/shunk031/ted-scraper',
    install_requires=['beautifulsoup4', 'lxml'],
    license='http://www.apache.org/licenses/LICENSE-2.0',
    test_suite='test.test_scraper'
)
