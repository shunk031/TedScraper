# TED Talks Scraper

[![Build Status](https://travis-ci.org/shunk031/ted-scraper.svg?branch=master)](https://travis-ci.org/shunk031/ted-scraper)

Scraper for [TED Talks](https://www.ted.com/talks).

## Requirement
	
* Python 3.5
* BeautifulSoup4
* lxml

## Usage

``` python

from ted_talks.scraper import TEDScraper

# available languages in TED Talks
print(TEDScraper.get_langurages())

# specify language
ts = TEDScraper(lang="en")

# get all talk links (as list object)
all_talk_links = ts.get_all_talk_links()

# get all talk topics (as list object)
all_talk_topics = ts.get_all_talk_topics(all_talk_links)

# get all talk transcript (as list object)
all_talk_transcripts = ts.get_all_transcripts(all_talk_links)

# dump talk-info (as json file)
ts.dump_talk_info(talk_url, save_dir)

# dump talk-info with all languages (as json file)
ts.dump_talk_info_al(talk_url, save_dir)

# dump all talk-info with all languages 
ts.dump_all_talk_info_al(save_dir)
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

Output result when using `TEDScraper#dump_talk_info()`.

``` json
{
	"posted_date" : "2016-01-01",
	"update_date" : "2016-01-02",
	"talk_title" : "talk-title",
	"talk_link" : "https://www.ted.com/talks/hoge",
	"talk_lang" : "en",
	"talk_topics" : ["topic1", "topic2", "topic3"],
	"transcript" : ["sentence1", "sentence2", "sentence3", "sentence4"],
	"time" : ["00:00", "00:01", "00:12"]
}
```


Output result when using `TEDScraper#dump_talk_info_al()`.

``` json
{
	"posted_date" : "2016-01-01",
	"update_date" : "2016-01-02",
	"talk_title" : "talk-title",
	"talk_link" : "https://www.ted.com/talks/hoge",
	"talk_topics" : ["topic1", "topic2", "topic3"],
	"transcript" : {
		"en" : ["sentence1", "sentence2", "sentence3", "sentence4"],
		"ja" : ["文1", "文2", "文3"],
		"cn" : ["句子1", "句子2", "句子3"]
	},
	"time" : ["00:00", "00:01", "00:12"]
}
```
