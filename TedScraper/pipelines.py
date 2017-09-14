# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TedscraperPipeline(object):
    def process_item(self, item, spider):
        return item


class FormatTarget(object):
    def process_item(self, item, spider, key):

        for k in item[key].keys():
            item[key][k] = self.format(item[key][k])

        return item

    def remove_tab(self, sentence):
        return [s.replace('\t', '') for s in sentence]

    def remove_newline_code(self, sentence):
        return [s.replace('\n', '') for s in sentence]

    def format(self, sentence):

        sentence = self.remove_tab(sentence)
        sentence = self.remove_newline_code(sentence)

        return sentence


class FormatTranscripts(FormatTarget):
    def process_item(self, item, spider):
        return super(FormatTranscripts, self).process_item(item, spider, key='transcripts')


class FormatTimes(FormatTarget):
    def process_item(self, item, spider):
        return super(FormatTimes, self).process_item(item, spider, key='times')
