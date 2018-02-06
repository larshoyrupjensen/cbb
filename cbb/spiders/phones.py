# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 15:34:47 2017

Classes and functions to find necessary information in phone history

@author: Lars
"""

import json
import datetime
import pandas as pd
from cbb.spiders.tools import normalise_unicode
import cbb.spiders.send_email
import cbb.spiders.mobiler 

JSON_FILE= "scraped_cbb_phones.json"
START_DATE = datetime.datetime(year=2017, month=12, day=16)

class PhoneData:
    def __init__(self, phone_dict):
        self.brand = normalise_unicode(phone_dict["brand"])
        self.model = normalise_unicode(phone_dict["model"])
        self.storage = normalise_unicode(phone_dict["storage"])
        self.price = phone_dict["price"]
        self.timestamp = phone_dict["timestamp"]
        self.id = (self.brand, self.model, self.storage)
        
    def __repr__(self):
        return (f"{self.brand} {self.model} {self.storage}, "
                f"pris: {self.price}, scraped on {self.timestamp}")
    

class PhoneModel:
    #Represents one unique phone model
    #Holds data about all scraped "instances" of this phone on cbb.dk
    scraped_dates = []
    
    def __init__(self, phone_data):
        self.id = phone_data.id
        self.brand = phone_data.brand
        self.model = phone_data.model
        self.storage = phone_data.storage
        self.phone_data = [phone_data,]
        self.is_active = None
        self.start_date = None
        self.end_date = None
        self.price_changes = []
    
    def add_phone(self, phone_data):
        self.phone_data.append(phone_data)
    
    def set_price_changes(self):
        #Finds all price changes
        #First, sort self.phone_data by date
        self.phone_data.sort(key=lambda x: x.timestamp)
        #Now, find all price changes and append to self.price_changes
        for i in range(len(self.phone_data) - 1):
            t = self.phone_data[i + 1].timestamp
            delta = self.phone_data[i + 1].price - self.phone_data[i].price
            if delta != 0:
                self.price_changes.append({t: delta})
    
    def set_status_and_dates(self):
        #Check if latest scrape of this model is in latest scrape of all models
        #How it is implemented:
        #if model timestamp is no more than 20 minutes older than newest
        #timestamp in all models, the phone is active. 
        model_datetimes_sorted = sorted(
                [datetime.datetime.strptime(
                pd.timestamp, "%Y-%m-%d %H:%M:%S") \
                for pd in self.phone_data])
        newest_all_phones = sorted(self.scraped_dates)[-1]
        newest_model = model_datetimes_sorted[-1]
        if newest_all_phones - newest_model < datetime.timedelta(minutes=20):
            self.is_active = True
            #Start date is earliest date in phone model, unless it is global
            #START_DATE. In the latter case, it remains None
            #End date remains None
            if model_datetimes_sorted[0].date() != START_DATE.date():
                self.start_date = model_datetimes_sorted[0]
        else:
            #Phone is not active and end date is last registered date
            #Start date remains None
            self.is_active = False
            self.end_date = model_datetimes_sorted[-1]
    
    def set_price(self):
        #Finds most recent price and sets it as phone's price
        self.price = sorted(
                self.phone_data, 
                key=lambda x: x.timestamp
                )[-1].price
    
    def finalize_model(self):
        self.set_price_changes()
        self.set_status_and_dates()
        self.set_price()
    
    def to_dicts(self):
        #Returns state of object in a dict for use in pandas HTML table
        return {"Brand": self.brand,
                "Model": self.model,
                "Storage": self.storage,
                "Price": self.price,
                "Active": self.is_active,
                "Entered list": str(self.start_date),
                "Exited list": str(self.end_date),
                "Latest price change": self.price_changes
                }
    
    def __repr__(self):
        return (f"{self.id}\n"
                f"start_date: {self.start_date}, \n"
                f"end_date: {self.end_date}\n")

def hello_world():
    print("Hello world")


class PhoneAnalyzer():
    def __init__(self, file, start_date):
        #This dictionary will hold all unique phone models
        self.phone_models = {}
        #Load all previously scraped phone data
        with open(file, "r") as fp:
            phone_dicts = json.loads(fp.read())
        filtered_phone_dicts = [pd for pd in phone_dicts if \
                    datetime.datetime.strptime(pd["timestamp"], "%Y-%m-%d %H:%M:%S")\
                    > start_date]
        for phone_dict in filtered_phone_dicts:
            # Build list of all scraped datetimes
            PhoneModel.scraped_dates.append(
                    datetime.datetime.strptime(phone_dict["timestamp"],
                                                          "%Y-%m-%d %H:%M:%S"))
            #Add phone_data to relevant model instance if it exists. Otherwise create
            phone_data = PhoneData(phone_dict)
            if phone_data.id in self.phone_models:
                self.phone_models[phone_data.id].add_phone(phone_data)
            else:
                phone_model = PhoneModel(phone_data)
                self.phone_models[phone_data.id] = phone_model
        #finalize all models in order to set variables
        for pm in self.phone_models.values():
            pm.finalize_model()

    def get_sorted_list_of_dicts(self):
        list_of_dicts = []
        for pm in self.phone_models.values():
            list_of_dicts.append(pm.to_dicts())
        pre_sorted = sorted(list_of_dicts, key=lambda x: (
                                                    x["Brand"],
                                                    x["Model"],
                                                    x["Price"],
                                                    ))
        return sorted(pre_sorted, key=lambda x: x["Active"], reverse=True)
        
    def get_ordered_columns(self):
        return [
                "Brand",
                "Model",
                "Storage",
                "Price",
                "Active",
                "Entered list",
                "Exited list",
                "Latest price change",
                ]

if __name__ == "__main__":
    pa = PhoneAnalyzer(JSON_FILE, START_DATE)
    dicts_for_pandas = pa.get_sorted_list_of_dicts()
    ordered_columns = pa.get_ordered_columns()
    df = pd.DataFrame(dicts_for_pandas)
    df = df[ordered_columns]
    df.index = df.index + 1

#    #Let's do some styling of the table
#    styles = [
#                dict(selector="", props=[
#                        ("border-spacing", "0"),                    
#                        ("font-family", "Arial"),
#                        ("font-size", "small"),
#                        ("font-weight", "normal"),
#                        ("text-align", "left"),
#                        ]),
#                dict(selector="th", props=[
#                        ("font-weight", "bold"),
#                        ("background-color", "skyblue"),
#                        ],),
#                dict(selector=".row_heading", props=[
#                        ("font-weight", "normal"),
#                        ("background-color", "transparent"),
#                        ],),
#            ]
#    html_table = "<html>"
#    html_table += df.style.format({"Price": "{:n}"}).\
#        bar(subset=["Price"], align="mid", color="orange").\
#        set_table_styles(styles).render()
#    html_table = html_table.replace("<style", "<head><style")
#    html_table = html_table.replace("</style>", "</style></head>")
#    html_table += "</html>"
    html_table = cbb.spiders.mobiler.MobilerSpider.df_to_html(df)
    with open("html_table.html", "w") as fp:
        fp.write(html_table)
    #html_table = df.to_html(border=0)
    #html_table = df.style.render()
    #Send html table as email
    #with open("html_table_edited.html", "r") as fp:
    #    html_table = fp.read()
#    cbb.spiders.send_email.send_email(
#            content=html_table, 
#            recipient="lars.hoyrup.jensen@gmail.com",
#            subject=f"CBB spider kørt TEST")
