# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sinaspider.items import InfoItem, TweetsItem, FollowsItem, FansItem
import pymysql
import json
import codecs
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('sina.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        print(insert_sql, params)
        cursor.execute(insert_sql, params)


class SinaspiderPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            passwd="15478xx",
            db='sina',
            charset='utf8'
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if isinstance(item, InfoItem):
            sql = """
            insert into information(_id, Nickname, Gender, Province, City, Signature, Birthday, Num_tweets, Num_follows, Num_fans, Sex_orientation, Authentication, URL) 
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (item["_id"], item["Nickname"], item["Gender"], item["Province"], item["City"], item["Signature"], item["Birthday"], item["Num_tweets"], item["Num_follows"], item["Num_fans"], item["Sex_orientation"], item["Authentication"], item["URL"])
            try:
                self.cursor.execute(sql, params)
                self.connect.commit()
            except Exception:
                pass
        if isinstance(item, TweetsItem):
            sql1 = """insert into tweets(_id, ID, Content, Pubtime, Cooridinate, Tools, Like, Comment, Transfer) 
                      values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params1 = (item["_id"], item["ID"], item["Content"], item["Pubtime"], item["Cooridinate"], item["Tools"], item["Like"], item["Comment"], item["Transfer"])
            try:
                self.cursor.execute(sql1, params1)
                self.connect.commit()
            except Exception:
                pass
        if isinstance(item, FollowsItem):
            sql2 = "insert into follows(_id, follows) values (%s, %s)"
            try:
                self.cursor.execute(sql2, (item["_id"], item["follows"]))
            except Exception:
                pass
        if isinstance(item, FansItem):
            sql3 = "insert into fans (_id, fans) values (%s, %s)"
            try:
                self.cursor.execute(sql3, (item["_id"], item["fans"]))
            except Exception:
                pass
        return item
