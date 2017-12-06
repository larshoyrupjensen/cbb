# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
#from scrapy_splash import SplashRequest

class MobilerSpider(scrapy.Spider):
    name = 'mobiler_no_splash'
    allowed_domains = ['cbb.dk']
    start_urls = ['http://cbb.dk/']

    def start_requests(self):
        #print("IN START_REQUESTS")
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        ng_click=response.xpath("//a[@data-name='Mobiltelefoner'][@data-category='topmenu'][@class='tracking_link_topmenu']/@ng-click").extract_first()
        mobiler_url=response.urljoin(ng_click.split("'")[1])
        self.logger.info(mobiler_url)
        #inspect_response(response, self)
        yield scrapy.Request(url=mobiler_url, 
                            callback=self.parse_list_of_mobiles)
        
    def parse_list_of_mobiles(self, response):
        #with open("mobiler.html", "wb") as f:
        #    f.write(response.body)
        #inspect_response(response, self)
        for phone in response.xpath("//button[@ng-href]"):
            #print(phone.xpath("@ng-href").extract_first())
            next_page=(response.urljoin(phone.xpath("@ng-href").extract_first()))
            self.logger.info(next_page)
            yield scrapy.Request(next_page, 
                                callback=self.parse_single_mobile, 
                                )
            #print(phone)
    def parse_single_mobile(self, response):
        #phone_info=response.xpath("//div[@class='product-overview ng-scope']")
        brand, storage=response.xpath(
                "//div[@class='product-overview ng-scope']//h3/text()").extract()
        model=response.xpath(
                "//div[@class='product-overview ng-scope']//h1/text()").extract_first()
        #nspect_response(response, self)
        #for li in phone_info.xpath("//li"):
        #    print(li)
        #print(phone_info.extract())
        #self.logger.info("I am here")
        self.logger.info("\n\nBrand: {0}, Model:{1}, Storage:{2}\n".format(brand, model, storage))
