# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from cbb.spiders.send_email import send_email
from cbb.spiders.tools import load_phones, save_phones
from cbb.spiders.tools import normalise_unicode
from cbb.spiders.phones import PhoneAnalyzer
import datetime
import pandas as pd
import unicodedata
import locale
import socket

JSON_FILE= "scraped_cbb_phones.json"
START_DATE = datetime.datetime(year=2017, month=12, day=16)

locale.setlocale(locale.LC_NUMERIC, "")

class MobilerSpider(scrapy.Spider):
    name = 'mobiler'
    allowed_domains = ['cbb.dk']
    start_urls = ['https://www.cbb.dk/']
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.date.today()
    hostname = socket.gethostname()
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
        old_phones=load_phones()
        all_phones = old_phones + self.phones
        save_phones(all_phones)
        pa = PhoneAnalyzer(JSON_FILE, START_DATE)
        dicts_for_pandas = pa.get_sorted_list_of_dicts()
        ordered_columns = pa.get_ordered_columns()
        df = pd.DataFrame(dicts_for_pandas)
        df = df[ordered_columns]
        df.index = df.index + 1
        

        #Send html table as email
        html_table = self.df_to_html(df)
        send_email(
                content=html_table, 
                recipient="lars.hoyrup.jensen@gmail.com",
                subject="CBB spider kørt {} på {}".format(
                        self.date,
                        self.hostname,)
                )
        #Also write html table to file for inspection
        with open("html_table.html", "w") as fp:
            fp.write(html_table)
        
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

    def highlight_new_row(s, columns, days=7):
        """
        Highlights entire rows with price changes newer than x days
        """
        is_new = pd.Series(data=False, index=s.index)
        is_new[columns] = pd.to_numeric(s.loc[columns]) < days
        return ["background-color: lightgreen" if is_new.any() else "" for v in is_new]

    def highlight_new(s, days=7):
        """
        Highlights cell with price changes newer than x days
        """
        is_new = pd.to_numeric(s) < days
        return ["background-color: lightgreen" if v else "" for v in is_new]

    def lowlight_inactive(s, columns):
        is_inactive = pd.Series(data=False, index=s.index)
        is_inactive[columns] = pd.to_numeric(s.loc[columns]) == False
        return ["color: lightgrey" if is_inactive.any() else "" for v in is_inactive]

    def highlight_recently_inactive(s, days=7, color="red"):
        """
        Higlights cells indicating that phone became inactive recently
        """
        td_days = pd.Timedelta(days, unit="d")
        s = pd.to_datetime(s).dt.date
        exited_recently = datetime.date.today() - s < td_days
        return [f"background-color: {color}" if v else "" for v in exited_recently]
    
    @classmethod
    def df_to_html(cls, df):
        #Converts Pandas Dataframe to HTML and styles it    
        #Also ensures <html> and <head> tags in HTML
        
        #First, remove None values from table
        df.replace("None", "", inplace=True)
        
        #Now, let's style the table
        styles = [
                dict(selector="", props=[
                        ("border-spacing", "0"),                    
                        ("font-family", "Arial"),
                        ("font-size", "small"),
                        ("font-weight", "normal"),
                        ("text-align", "left"),
                        ]),
                dict(selector="th", props=[
                        ("font-weight", "bold"),
                        ("background-color", "skyblue"),
                        ],),
                dict(selector=".row_heading", props=[
                        ("font-weight", "normal"),
                        ("background-color", "transparent"),
                        ("color", "lightgrey"),
                        ("font-style", "italic"),                        
                        ],),
                dict(selector=".col7", props=[
                        ("text-align", "center"),
                        ],),
                dict(selector=".col8", props=[
                        ("text-align", "right"),
                        ],),
                dict(selector="tr:hover",props=[
                        ("background-color", "lightgrey")
                        ],),
                ]
        html_table = "<html>"
        html_table += df.style.format({"Price": "{:n}"}).\
            bar(subset=["Price"], align="mid", color="orange").\
            apply(cls.highlight_new, 
                  days=12,
                  subset=["Latest change, date",],
                  axis=1).\
            apply(cls.highlight_recently_inactive,
                  days=14,
                  color="cyan",
                  subset=["Exited list",],
                  axis=1).\
                  set_table_styles(styles).render()
        html_table = html_table.replace("<style", "<head><style")
        html_table = html_table.replace("</style>", "</style></head>")
        html_table += "</html>"
        return html_table

#            apply(cls.lowlight_inactive, columns="Active", axis=1).\
        

