# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
import re
import datetime


class CustomItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def getprovince(value):
    place = re.findall('地区[:|：](.*?)[<br>|<br/>]', value)
    try:
        a = place[0].split(" ")
        place = a[0]
    except Exception as e:
        place = "Lone"
    return place


def getcity(value):
    place = re.findall('地区[:|：](.*?)[<br>|<br/>]', value)
    try:
        a = place[0].split(" ")
        if len(a) > 1:
            place = a[1]
    except Exception as e:
        place = "Lone"
    return place


def get_num(value):
    return value

def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except Exception as e:
        create_date = "1900-1-1"
    return create_date


def get_content(value):
    pass

def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return str(nums)


class InfoItem(Item):
    """ 个人信息 """
    _id = Field()  # 用户ID
    Nickname = Field(
        input_processor=MapCompose(lambda x: re.findall('昵称[:|：](.*?)[<br/>|<br>]', x))
    )  # 昵称
    Gender = Field(
        input_processor=MapCompose(lambda x: re.findall('性别[:|：](.*?)[<br/>|<br>]', x))
    )  # 性别
    Province = Field(
        input_processor=MapCompose(getprovince)
    )  # 所在省
    City = Field(
        input_processor=MapCompose(getcity)
    )  # 所在城市
    Signature = Field(
        input_processor=MapCompose(lambda x: re.findall('简介[:|：](.*?)[<br>|<br/>]', x))
    )  # 个性签名
    Birthday = Field(
        input_processor=MapCompose(lambda x: re.findall('生日[:|：](.*?)[<br>|<br/>]', x), date_convert)
    )  # 生日
    Num_tweets = Field(
        input_processor=MapCompose(lambda x: re.findall('.*微博\[(\d+)\]', x), get_num)
    )  # 微博数
    Num_follows = Field(
        input_processor=MapCompose(lambda x: re.findall('.*关注\[(\d+)\]', x), get_num)
    )  # 关注数
    Num_fans = Field(
        input_processor=MapCompose(lambda x: re.findall('.*粉丝\[(\d+)\]', x), get_num)
    )  # 粉丝数
    Authentication = Field(
        input_processor=MapCompose(lambda x: re.findall('.*认证信息[:|：](.*?)[<br>|<br/>]', x))
    )  # 认证信息
    URL = Field(
        input_processor=MapCompose(lambda x: re.findall('([a-zA-z_]+://weibo.com.*?)<br/>', x))
    )  # 首页链接

    def get_insert_sql(self):
        sql = """
              insert into information(_id, Nickname, Gender, Province, City, Signature, Birthday, Num_tweets, Num_follows, Num_fans, Authentication, URL) 
              values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
        if "Nickname" not in self:
            self["Nickname"] = " "
        if "Gender" not in self:
            self["Gender"] = "N/A"
        if "Province" not in self:
            self["Province"] = "N/A"
        if "City" not in self:
            self["City"] = "N/A"
        if "Signature" not in self:
            self["Signature"] = "N/A"
        if "Birthday" not in self:
            self["Birthday"] = "1900-1-1"
        if "Authentication" not in self:
            self["Authentication"] = "N/A"
        if "URL" not in self:
            self["URL"] = "https://weibo.cn/" + self["_id"]
        if "Num_tweets" not in self:
            self["Num_tweets"] = "0"
        if "Num_fans" not in self:
            self["Num_fans"] = "0"
        if "Num_follows" not in self:
            self["Num_follows"] = "0"
        params = (self["_id"], self["Nickname"], self["Gender"], self["Province"], self["City"], self["Signature"], self["Birthday"], self["Num_tweets"], self["Num_follows"], self["Num_fans"], self["Authentication"], self["URL"])
        return sql, params

# TODO: 统一格式
class TweetsItem(Item):
    """ 微博信息 """
    _id = Field()  # 用户ID
    ID = Field()  # 微博ID
    Content = Field(
    )  # 微博内容
    Pubtime = Field(
        input_processor=MapCompose(lambda x: (x.split("来自"))[0])
    )  # 发表时间
    Cooridinate = Field(
        input_processor=MapCompose(lambda x: re.findall(".*center=(.*)&", x))
    )  # 定位坐标
    Tools = Field(
        input_processor=MapCompose(lambda x: (x.split("来自"))[1])
    )  # 发表工具/平台
    Like = Field(
        input_processor=MapCompose(lambda x: re.findall('.*赞\[(.*?)\]', x), get_num)
    )  # 点赞数
    Comment = Field(
        input_processor=MapCompose(lambda x: re.findall('.*评论\[(.*?)\]', x), get_num)
    )  # 评论数
    Transfer = Field(
        input_processor=MapCompose(lambda x: re.findall('.*转发\[(.*?)\]', x), get_num)
    )  # 转载数

    def get_insert_sql(self):
        sql = """insert into tweets(_id, ID, Content, Pubtime, Cooridinate, Tools, Like_num, Comment_num, Transfer_num) 
                              values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
        if "Cooridinate" not in self:
            self["Cooridinate"] = "N/A"
        if "Tools" not in self or "Tools" == "":
            self["Tools"] = "N/A"
        if "Like" not in self:
            self["Like"] = 0
        if "Comment" not in self:
            self["Comment"] = 0
        if "Transfer" not in self:
            self["Transfer"] = 0
        if "ID" not in self:
            self["ID"] = "N/A"
        if "Content" not in self:
            self["Content"] = "N/A"
        if "Pubtime" not in self:
            self["Pubtime"] = "N/A"
        params = (self["_id"], self["ID"], self["Content"], self["Pubtime"], self["Cooridinate"], self["Tools"], self["Like"], self["Comment"], self["Transfer"])
        return sql, params


class FollowsItem(Item):
    """ 关注人列表 """
    _id = Field()  # 用户ID
    follows = Field(
        input_processor=MapCompose(get_nums)
    )  # 关注

    def get_insert_sql(self):
        sql = "insert into follows_tbl(_id, follows_id) values (%s, %s)"
        params = (self["_id"], self["follows"])
        return sql, params

class FansItem(Item):
    """ 粉丝列表 """
    _id = Field()  # 用户ID
    fans = Field(
        input_processor=MapCompose(get_nums)
    )  # 粉丝

    def get_insert_sql(self):
        sql = "insert into fans_tbl (_id, fans_id) values (%s, %s)"
        params = (self["_id"], self["fans"])
        return sql, params