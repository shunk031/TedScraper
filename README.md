# TED Talks Scraper

Scraper for [TED Talks](https://www.ted.com/talks).

## Requirement
	
* Python 3.5
* BeautifulSoup

## Usage

``` python

from ted_scraper import TEDScraper

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

# dump talk-info json file
ts.dump_talk_info(target_url)

# dump talk-info with all languages json file
# ts.dump_talk_info_al(target_url)
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

Output result when using `dump_talk_info()`.

``` json
{
	"Posted Date" : "2016-01-01",
	"Updated Date" : "2016-01-02",
	"Talk Title" : "talk-title",
	"Talk Link Adress" : "https://www.ted.com/talks/hoge",
	"Topics" : ["topic1", "topic2", "topic3"],
	"Transcript Text" : ["sentence1", "sentence2", "sentence3", "sentence4"]
}
```


Output result when using `dump_talk_info_al()`.

``` json
{
	"Posted Date" : "2016-01-01",
	"Updated Date" : "2016-01-02",
	"Talk Title" : "talk-title",
	"Talk Link Adress" : "https://www.ted.com/talks/hoge",
	"Topics" : ["topic1", "topic2", "topic3"],
	"Transcript Text" : {
		en : ["sentence1", "sentence2", "sentence3", "sentence4"],
		ja : ["文1", "文2", "文3"],
		cn : ["句子1", "句子2", "句子3"]
	}
}
```
