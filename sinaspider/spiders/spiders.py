from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from sinaspider.items import InfoItem, TweetsItem, FollowsItem, FansItem, CustomItemLoader


class Spider(CrawlSpider):
    name = "sinaspider"
    host = "https://weibo.cn"
    start_urls = [
        5878675399, 5676304901, 5871897095, 2139359753, 5579672076, 2517436943, 5780802073, 2159807003, 5187664653,
        1756807885, 3378940452, 5762793904, 1885080105, 5778836010, 5722737202, 3105589817, 5882481217, 5831264835,
        2717354573, 3637185102, 1934363217, 5336500817, 1431308884, 5818747476, 5073111647, 5398825573, 2501511785,
    ]
    scrawl_ID = set(start_urls)
    finish_ID = set()

    def start_requests(self):
        while self.scrawl_ID.__len__():
            ID = self.scrawl_ID.pop()
            self.finish_ID.add(ID)
            ID = str(ID)

            url_follows = "https://weibo.cn/%s/follow" % ID
            url_fans = "https://weibo.cn/%s/fans" % ID
            url_tweets = "https://weibo.cn/%s/profile?filter=1&page=1" % ID
            url_info0 = "https://weibo.cn/attgroup/opening?uid=%s" % ID

            yield Request(url=url_follows, meta={"ID": ID}, callback=self.parse4)
            yield Request(url=url_fans, meta={"ID": ID}, callback=self.parse3)
            yield Request(url=url_info0, meta={"ID": ID}, callback=self.parse0)
            yield Request(url=url_tweets, meta={"ID": ID}, callback=self.parse2)

    def parse0(self, response):
        """ 
        抓取个人信息1
        微博数，关注数，粉丝数，以及用户id
        """
        selector = Selector(response)
        item_loader = CustomItemLoader(item=InfoItem(), selector=selector, response=response)
        item_loader.add_xpath("Num_tweets", '/html/body//div[@class="tip2"]/a[1]/text()')
        item_loader.add_xpath("Num_follows", '/html/body//div[@class="tip2"]/a[2]/text()')
        item_loader.add_xpath("Num_fans", '/html/body//div[@class="tip2"]/a[3]/text()')
        item_loader.add_value("_id", response.meta["ID"])
        url_info1 = "https://weibo.cn/%s/info" % response.meta["ID"]
        infoitems = item_loader.load_item()
        yield Request(url=url_info1, meta={"item": infoitems},
                      callback=self.parse1)

    def parse1(self, response):
        """ 
        抓取个人信息2
        昵称，性别，地区（省份，城市），个性签名，生日，性取向，婚姻状况，首页链接
        """
        selector = Selector(response)
        item_loader = CustomItemLoader(item=response.meta["item"], selector=selector, response=response)
        item_loader.add_xpath("Nickname", '/html/body//div[@class="c"][3]')
        item_loader.add_xpath("Gender", '/html/body//div[@class="c"][3]')
        item_loader.add_xpath("Province", '/html/body//div[@class="c"][3]')
        item_loader.add_xpath("City", '/html/body//div[@class="c"][3]')
        item_loader.add_xpath("Signature", '/html/body//div[@class="c"][3]')
        item_loader.add_xpath("Birthday", '/html/body//div[@class="c"][3]')
        item_loader.add_xpath("Authentication", '/html/body//div[@class="c"][3]')
        item_loader.add_xpath("URL", '/html/body/div[@class="c"][last()-2]')

        infoitems = item_loader.load_item()

        yield infoitems

    def parse2(self, response):
        """
        抓取微博数据 
        每条微博ID，内容，坐标，点赞数，转发数，评论数，使用的工具，发布的时间，
        """
        selector = Selector(response)
        tweets = selector.xpath('/html/body/div[@class="c" and @id]')
        for tweet in tweets:
            item_loader = CustomItemLoader(item=TweetsItem(), selector=tweet, response=response)
            item_loader.add_value("_id", response.meta["ID"])
            item_loader.add_xpath("ID", './@id')
            item_loader.add_xpath("Content", 'div/span[@class="ctt"]/text()')
            item_loader.add_xpath("Pubtime", 'div[last()]/span[@class="ct"]/text()')
            item_loader.add_xpath("Cooridinate", 'div[last()]/a[@href]')
            item_loader.add_xpath("Tools", 'div[last()]/span[@class="ct"]/text()')
            item_loader.add_xpath("Like", 'div[last()]/a[last()-3][@href]/text()')
            item_loader.add_xpath("Transfer", 'div[last()]/a[last()-2][@href]/text()')
            item_loader.add_xpath("Comment", 'div[last()]/a[last()-1][@href]/text()')

            tweetsitem = item_loader.load_item()

            yield tweetsitem
        url_next = selector.xpath('//*[@id="pagelist"]/form/div/a[text()="下页"/@href').extract()
        if url_next:
            yield Request(url=self.host+url_next[0])
        else:
            print("No more!")
    def parse3(self, response):
        """ 
        抓取粉丝 
        """
        selector = Selector(response)
        fans = selector.xpath('/html/body//table//tr/td/a[text()="关注她" or text()="关注他" or text()="已关注"]')
        for fan in fans:
            item_loader = CustomItemLoader(item=FansItem(), selector=fan, response=response)
            item_loader.add_value("_id", response.meta["ID"])
            item_loader.add_xpath("fans", './@href')
            fansitem = item_loader.load_item()

            yield fansitem
        url_next = selector.xpath('//*[@id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"]}, callback=self.parse3)
        else:
            print("There's no more page.")

    def parse4(self, response):
        """ 
        抓取关注 
        """
        selector = Selector(response)
        follows = selector.xpath('/html/body//table//tr/td/a[text()="关注他" or text()="关注她" or text()="已关注"]')
        for follow in follows:
            item_loader = CustomItemLoader(item=FollowsItem(), selector=follow, response=response)
            item_loader.add_value("_id", response.meta["ID"])
            item_loader.add_xpath("follows", './@href')
            followsitem = item_loader.load_item()

            yield followsitem
        url_next = selector.xpath('//*[@id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], meta={"ID": response.meta["ID"], "item": followsitem}, callback=self.parse4)
        else:
            print("There's no more page.")
