# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


#class DoubanmoivePipeline(object):
#    def process_item(self, item, spider):
#        return item

import json
import codecs

from scrapy import log
from twisted.enterprise import adbapi
from scrapy.http import Request

import MySQLdb
import MySQLdb.cursors

class DoubanmoivePipeline(object):

    def __init__(self):
        self.file = codecs.open('douban_data.json', mode='wb', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))

        return item
class DoPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                db = 'liu',
                user = 'root',
                passwd = '',
                cursorclass = MySQLdb.cursors.DictCursor,
                charset = 'utf8',
                use_unicode = False
        )
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        return item

    def _conditional_insert(self,tx,item):
        tx.execute("select * from doubanmoive where m_name= %s",(item['name'][0],))
        result=tx.fetchone()
        log.msg(result,level=log.DEBUG)
        print result
        if result:
            log.msg("Item already stored in db:%s" % item,level=log.DEBUG)
        else:
            classification=actor=''
            lenClassification=len(item['classification'])
            lenActor=len(item['actor'])
            for n in xrange(lenClassification):
                classification+=item['classification'][n]
                if n<lenClassification-1:
                    classification+='/'
            for n in xrange(lenActor):
                actor+=item['actor'][n]
                if n<lenActor-1:
                    actor+='/'

            tx.execute(\
                "insert into doubanmoive (m_name,m_year,m_score,m_director,m_classification,m_actor) values (%s,%s,%s,%s,%s,%s)",\
                 ("".join(item['name']), "".join(item['year']), "".join(item['score']), "".join(item['director']), classification, actor))
            log.msg("Item stored in db: %s" % item, level=log.DEBUG)

    def handle_error(self, e):
        log.err(e)
