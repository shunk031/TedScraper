# TED Talks Scraper

Scraper for [TED Talks](https://www.ted.com/talks).

## Requirement
	
* Python 3.5
* BeautifulSoup

## Usage

``` python

from ted_scraper import TEDScraper

base_url = "https://www.ted.com/talks"

# specify base URL and language
ts = TEDScraper(base_url, lang="en")

# get all talk links
ts.get_all_talk_links()

# get all talk topics
ts.get_all_talk_topics()
```

## Outputs

* Talk Title
* Talk Link Address
* Language
* Topics
* Transcript Text
