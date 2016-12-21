# X-Rates crawler
This is a simple Srapy python crawler to get USD currency exchange rates from the x-rates.com.
We will use here scrapy crawler and sqlite3 database in which we'll save all the crawled data.
This Scrapy crawler is written in just one simple file and fully commented in order to make it as clear as possible.
The crawler is run from python script (against proper way of building Scrapy crawler - directory hierarchy, runned by scrapy crawl xxx)

To make Scrapy working from just one file, first we have to define Scrapy Items to be crawled:
```
class XratesItem(scrapy.Item):  # Scrapy class where data will be filled
    date = scrapy.Field()   # Current date
    name = scrapy.Field()   # Name of the currency
    sell = scrapy.Field()   # Sell price
    buy = scrapy.Field()    # Buy price
```

This is our crawler spider class:
```
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
```

And we will store our crawled data in sqlite3 database 
```
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
```

Finally main method for run the crawling
```
if __name__ == '__main__':
    db = Database()
    db.constructDB()  # This line run just the first time for constructing our database

    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'}) # Configuring logging messages while crawling
    runner = CrawlerRunner()
    d = runner.crawl(XratesSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # The script will block here until the crawling is finished

    db.close()  # Don't forget to close database connection when we're finished
```


