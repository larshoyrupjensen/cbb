# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
import unicodedata
#from scrapy.mail import MailSender
import locale
import os
from . import send_email
from .tools import find_changed_phones
import json
import datetime
import pandas as pd

#This doesn't work on Linux, so disabled
#locale.setlocale(locale.LC_ALL, 'Danish')
print(os.path.abspath(os.path.curdir))


class MobilerSpider(scrapy.Spider):
    name = 'mobiler'
    allowed_domains = ['cbb.dk']
    start_urls = ['http://cbb.dk/']
    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    phones=[]

    def start_requests(self):
        script = """
        function main(splash)
            assert(splash:go(splash.args.url))
            assert(splash:wait(2.0))
            return splash:html()
        end
        """
        for url in self.start_urls:
            yield SplashRequest(url=url, 
                                callback=self.parse, 
                                endpoint="execute",
                                args={"lua_source": script})

    def closed(self, spider):       
        #sort scraped phones by 1) brand and 2) price
        def phone_sorter(phone):
            if phone["price"] == None:
                return (phone["brand"], 0)
            else:
                return (phone["brand"], phone["price"])
        self.phones = sorted(self.phones, 
                             key = phone_sorter)
                             #key = lambda k: (k["brand"], k["price"]))
        df = pd.DataFrame(self.phones)
        d1 = dict(selector="th", props=[('text-align', 'left')])
        d2 = dict(selector="style", props=[('text-align', 'left')])
        df.index = df.index + 1
        html = df.style.set_table_styles([d1, d2])\
            .render()
            #.set_properties(**{'text-align': 'left', 'width':'10cm'})\
        #new_phones_as_html = df.to_html(border=0)
        new_phones_as_html = html
        with open("new_phones_table.html", "w") as fp:
            fp.write(new_phones_as_html)

        phones=load_phones()
        changes=find_changed_phones(self.phones, phones)
        df = pd.DataFrame(changes)
        changes_as_html = df.to_html(col_space=100, border=0)
        phones=phones + self.phones
        save_phones(phones)
        body="ÆNDREDE TELEFONER\n\n"
        body = ""
        body += changes_as_html
        #body += "\n\nSKRABEDE TELEFONER\n\n"
        body += new_phones_as_html
        send_email.send_email(
                content=body, 
                recipient="lars.hoyrup.jensen@gmail.com",
                subject="CBB spider kørt {}".format(self.timestamp))
        
    def parse(self, response):
        script = """
            function main(splash, args)
              assert(splash:go(args.url))
              assert(splash:wait(2.5))
              element = splash:select("#menufication-page-holder > div.landingpage.item-template.overview-template > div.products-section > div > div > div.col-xs-12.text-center > button")
              more_to_show = true
              while more_to_show do
              	if pcall(show_more, splash, element) then
                    more_to_show = true
              	else
                    more_to_show = false
              	end
              end
            
              return {
                html = splash:html(),
              }
            end
            
            function show_more(splash, element)
              ok, reason = element:mouse_click()
              splash:wait(2.5)
            end  
        """
        #inspect_response(response, self)
        ng_click=response.xpath("//a[@data-name='Mobiltelefoner'][@data-category='topmenu'][@class='tracking_link_topmenu']/@ng-click").extract_first()
        mobiler_url=response.urljoin(ng_click.split("'")[1])
        self.logger.info(mobiler_url)
        yield SplashRequest(url=mobiler_url, 
                            callback=self.parse_list_of_mobiles, 
                            endpoint="execute",
                            args={"lua_source": script})
        
    def parse_list_of_mobiles(self, response):
        #self.logger.info("Inde i parse_list_of_mobiles, url'en er {}".format(response.url))
        script = """
        function main(splash, args)
          assert(splash:go(args.url))
          assert(splash:wait(12.5))
          return {
            html = splash:html()
          }
        end
        """
        for phone in response.xpath("//button[@ng-href]"):
            #print(phone.xpath("@ng-href").extract_first())
            next_page=(response.urljoin(phone.xpath("@ng-href").extract_first()))
            self.logger.info(next_page)
            yield SplashRequest(url=next_page, 
                                callback=self.parse_single_mobile, 
                                endpoint="execute",
                                args={"lua_source": script})

    def parse_single_mobile(self, response):
        #if "iphone-6s" in response.url.lower():
        #    inspect_response(response, self)
        #if response.xpath(
        #        "//div[@class='product-overview ng-scope']//h1/text()")\
        #        .extract_first() == "Mate 10 Lite":
        #            inspect_response(response, self)
        try:
            brand, storage=response.xpath(
                    "//div[@class='product-overview ng-scope']//h3/text()").extract()
        except ValueError:
            brand = response.xpath(
                    "//div[@class='product-overview ng-scope']//h3/text()").extract_first()
            storage = None
        model=response.xpath(
                "//div[@class='product-overview ng-scope']//h1/text()").extract_first()
        try:
            price_string=unicodedata.normalize("NFKD", 
                                           response.xpath(
                "//text()[contains(.,'Telefonens pris')]").extract_first())
            price=int(''.join(filter(str.isdigit, price_string)))
        except TypeError:
            #price = "<UNKNOWN>"
            price = None
        mobile={"brand": brand, 
                "storage": storage, 
                "model": model, 
                "price": price,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.logger.info(
                "\n\nBrand: {0}, Model:{1}, Storage:{2}, Price:{3}, Timestamp:{4}\n".format(brand, model, storage, price, self.timestamp))
        self.phones.append(mobile)

def load_phones():
    JSON_FILE="scraped_cbb_phones.json"
    try:
        with open(JSON_FILE, "r") as fp:
            phones=json.load(fp)
        return phones
    except FileNotFoundError:
        return []
    

def save_phones(phones):
    JSON_FILE="scraped_cbb_phones.json"
    with open(JSON_FILE, "w") as fp:
        json.dump(phones, fp)
        
        
"""
LUA SCRIPT
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(2.5))
  splash:set_viewport_size(1366, 4000)
  local element = splash:select("#menufication-page-holder > div.landingpage.item-template.overview-template > div.products-section > div > div > div.col-xs-12.text-center > button")
  while element do
    element:mouse_click()
    splash:wait(2)
  end  
  --local bounds = element:bounds()
  --assert(element:mouse_click{x=bounds.width/2, y=bounds.height/2})
  assert(element:mouse_click())
  assert(splash:wait(1))
  return {
    html = splash:html(),
    png = splash:png(),
    har = splash:har(),
  }
end
"""





"""
FAILS ON 6TH CLICK, OK IF ONLY 5 CLICKS
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(1.5))
  --splash:set_viewport_full()
  splash:set_viewport_size(1024, 5500)  
  element = splash:select("#menufication-page-holder > div.landingpage.item-template.overview-template > div.products-section > div > div > div.col-xs-12.text-center > button")
	ok, reason = element:mouse_click()
 	splash:wait(1)
	ok, reason = element:mouse_click()
 	splash:wait(1)
	ok, reason = element:mouse_click()
 	splash:wait(1)
	ok, reason = element:mouse_click()
 	splash:wait(1)
	ok, reason = element:mouse_click()
 	splash:wait(1)
	ok, reason = element:mouse_click()
 	splash:wait(1)
  
  return {
    html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
  }
end"""


"""
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(1.5))
  --splash:set_viewport_full()
  splash:set_viewport_size(1024, 5500)  
  element = splash:select("#menufication-page-holder > div.landingpage.item-template.overview-template > div.products-section > div > div > div.col-xs-12.text-center > button")
	ok, reason = element:mouse_click()
  splash:wait(1)
  ok, reason = element:mouse_click()
  splash:wait(1)
  ok, reason = element:mouse_click()
  splash:wait(1)
  --ok, reason = element:mouse_click()
  --splash:wait(1)
  --ok, reason = element:mouse_click()
 	--splash:wait(1)
  --ok, reason = element:mouse_click()
 	--splash:wait(1)

--  while ok do
--    ok, reason = element:mouse_click()
    --ok, reason = element:mouse_click()
-- 		splash:wait(1)
    --ok = nil
--  end
	--ok, reason = element:mouse_click()
 	--splash:wait(1)
  return {
    --html = splash:html(),
    png = splash:png(),
    --har = splash:har(),
    json = {
      --key1 = splash:evaljs("document.pfCtrl.limit"), 
      key3 = splash:evaljs("document.title"),
      key2=ok}
  }
end
"""


"""
THIS WORKS!
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(2.5))
  --splash:set_viewport_full()
  splash:set_viewport_size(1024, 5500)  
  element = splash:select("#menufication-page-holder > div.landingpage.item-template.overview-template > div.products-section > div > div > div.col-xs-12.text-center > button")
  more_to_show = true
  while more_to_show do
  	if pcall(show_more, splash, element) then
      more_to_show = true
  	else
      more_to_show = false
  	end
  end

  return {
    html = splash:html(),
  }
end

function show_more(splash, element)
  ok, reason = element:mouse_click()
  splash:wait(2)
end  
"""