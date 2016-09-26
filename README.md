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

* Posted Date
* Update Date
* Talk Title
* Talk Link Address
* Language
* Topics
* Transcript Text

### Output Example

``` json
{
	"Posted Date" : "2016-01-01",
	"Updated Date" : "2016-01-02",
	"Talk Title" : "talk-title",
	"Talk Link Adress" : "https://www.ted.com/talks/hoge?language=en",
	"Language" : "en",
	"Topics" : ["topic1", "topic2", "topic3"],
	"Transcript Text" : ["sentence1", "sentence2", "sentence3", "sentence4"]
}
```

