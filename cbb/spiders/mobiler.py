# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
import unicodedata
from .send_email import send_email
from .tools import find_changed_phones, phone_sorter, load_phones, save_phones
import datetime
import pandas as pd


class MobilerSpider(scrapy.Spider):
    name = 'mobiler'
    allowed_domains = ['cbb.dk']
    start_urls = ['https://www.cbb.dk/']
    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    phones=[] #List to hold scraped phones

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
        #On shutdown, sort scraped phones by 1) brand, 2) model and 3) price
        self.phones = sorted(self.phones, 
                             key = phone_sorter)

        df = pd.DataFrame(self.phones)
        d1 = dict(selector="th", props=[('text-align', 'left')])
        d2 = dict(selector="style", props=[('text-align', 'left')])
        df.index = df.index + 1
        new_phones_as_html = df.style.set_table_styles([d1, d2])\
            .render()
            #.set_properties(**{'text-align': 'left', 'width':'10cm'})\
        with open("new_phones_table.html", "w") as fp:
            fp.write(new_phones_as_html)

        old_phones=load_phones()
        changes=find_changed_phones(self.phones, old_phones)
        df = pd.DataFrame(changes)
        changes_as_html = df.to_html(col_space=100, border=0)
        all_phones = old_phones + self.phones
        save_phones(all_phones)
        body = changes_as_html
        body += new_phones_as_html
        send_email(
                content=body, 
                recipient="lars.hoyrup.jensen@gmail.com",
                subject="CBB spider kørt {}".format(self.timestamp))
        
    def parse(self, response):
        #The Lua script below is used by parse_list_of_mobiles()
        #It clicks "Vis flere" button until error which is caught. 
        #Then we are sure all phones are shown on page
        script = """
            function main(splash, args)
              assert(splash:go(args.url))
              assert(splash:wait(2.5))
              element = splash:select("#menufication-page-holder > \
                  div.landingpage.item-template.overview-template > \
                  div.products-section > div > div > \
                  div.col-xs-12.text-center > button")
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
        #Now let's find URL for page with mobile phones for sale
        ng_click = response.xpath("//a[@data-name='Mobiltelefoner']"
                                  "[@data-category='topmenu']"
                                  "[@class='search-input--active "
                                  "tracking_link_topmenu']/@ng-click")\
                                  .extract_first()
        mobiler_url = response.urljoin(ng_click.split("'")[1])
        self.logger.info(mobiler_url)
        
        yield SplashRequest(url=mobiler_url, 
                            callback=self.parse_list_of_mobiles, 
                            endpoint="execute",
                            args={"lua_source": script})
        
    def parse_list_of_mobiles(self, response):
        script = """
        function main(splash, args)
          assert(splash:go(args.url))
          assert(splash:wait(2))
          return {
            html = splash:html()
          }
        end
        """
        
        #Scrape each individual phone page
        for phone in response.xpath("//button[@ng-href]"):
            phone_page=(response.urljoin(
                    phone.xpath("@ng-href").extract_first()))
            self.logger.info(phone_page)
            yield SplashRequest(url=phone_page, 
                                callback=self.parse_single_mobile, 
                                endpoint="execute",
                                args={"lua_source": script})

    def parse_single_mobile(self, response):
        #Strip relevant data for each phone
        phone_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        brand = response.xpath(
                '//*[@id="menufication-page-holder"]/'
                'div[1]/div/div[1]/h3//text()')\
                .extract_first()
        #The crazy Xpath selector below is found in Chrome Dev Tools
        storage = response.xpath(
                '//*[@id="menufication-page-holder"]/div[1]/div/div[3]/div/'
                'div[2]/div[1]//text()').extract_first()
        model=response.xpath('//*[@id="menufication-page-holder"]/'
                             'div[1]/div/div[1]/h1//text()').extract_first()
        price_string=unicodedata.normalize("NFKD", response.xpath(
                '//*[@id="menufication-page-holder"]/div[1]/div/div[3]/div/'
                'div[8]/div[2]/div/div[2]/text()').extract_first())
        price = int(''.join(filter(str.isdigit, price_string)))
        mobile = {"brand": brand, 
                  "storage": storage, 
                  "model": model, 
                  "price": price,
                  "timestamp": phone_timestamp}
        self.logger.info(
                "\n\nBrand: {0}, Model:{1}, Storage:{2}, Price:{3}, \
                Timestamp:{4}\n".format(brand, model, storage, price, 
                phone_timestamp))
        self.phones.append(mobile)

