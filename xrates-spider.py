import scrapy
from datetime import datetime, timedelta
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

import sqlite3
import os

class Database():   # Database class with basic methods
    def __init__(self):
        self.conn = sqlite3.connect(os.getcwd() + '/xrates.db') # Creating database and its connection in current working directory
        self.c = self.conn.cursor()

    def constructDB(self):
        self.c.execute("CREATE TABLE usd (date text, name text, sell real, buy real)")

    def execute(self, command, parameters=()):
        self.c.execute(command, parameters)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

class XratesItem(scrapy.Item):  # Scrapy class where data will be filled
    date = scrapy.Field()   # Current date
    name = scrapy.Field()   # Name of the currency
    sell = scrapy.Field()   # Sell price
    buy = scrapy.Field()    # Buy price

class XratesSpider(scrapy.Spider):
    name = "Xrates" # Name of the crawler
    baseURL = "http://x-rates.com/historical/?from=USD&amount=1&date="  # Add date in format 2016-12-12
    beginDate = datetime(2016, 12, 1).date()    # Crawl from this date
    endDate = datetime.now().date() # Crawl till this date

    def start_requests(self):
        while self.beginDate <= self.endDate:
            actURL = self.baseURL + str(self.beginDate) # Construct URL for current crawling date
            self.beginDate += timedelta(days=1) # Increment date by one day
            yield scrapy.Request(url=actURL,callback=self.parse) # Request URL and in callback parse crawled page

    def parse(self, response):
        date = response.url.split("=")[-1]
        for item in response.xpath("//table[@class='ratesTable']/tbody/tr"):    # In for loop extract all the wanted data from xrates webpage table
            res = XratesItem()
            res['date'] = date  # Current date
            res['name'] = item.xpath('td[1]/text()').extract()[0]   # Currency name
            res['sell'] = item.xpath('td[2]/a/text()').extract()[0] # Sell price
            res['buy'] = item.xpath('td[3]/a/text()').extract()[0]  # Buy price
            db.execute("INSERT INTO usd VALUES (?, ?, ?, ?)", (res['date'], res['name'], res['sell'], res['buy'])) # Insert the row of data
            db.commit() # Save the changes

if __name__ == '__main__':
    db = Database()
    db.constructDB()  # This line run just the first time for constructing our database

    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'}) # Configuring logging messages while crawling
    runner = CrawlerRunner()
    d = runner.crawl(XratesSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # The script will block here until the crawling is finished

    db.close()  # Don't forget to close database connection when we're finished