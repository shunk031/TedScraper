# TED Talks Scraper

Scraper for [TED Talks](https://www.ted.com/talks).

## Requirement
	
* Python 3.5
* BeautifulSoup

## Usage

``` python

from ted_scraper import TEDScraper

base_url = "https://www.ted.com/talks"

ts = TEDScraper(base_url)
ts.get_all_talk_links()
ts.get_all_talk_topics()
```

## Outputs

* Talk Title
* Talk Link Address
* Language
* Topics
* Transcript Text
