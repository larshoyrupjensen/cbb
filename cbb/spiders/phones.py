# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 15:34:47 2017

Classes and functions to find necessary information in phone history

@author: Lars
"""

import json
import datetime
import os
from cbb.spiders.tools import normalise_unicode


print(f"Current dir: {os.path.abspath(os.path.curdir)}")
JSON_FILE= "scraped_cbb_phones.json"
START_DATE = datetime.datetime(year=2017, month=12, day=16)
phone_models = {}

class PhoneData:
    
    def __init__(self, phone_dict):
        self.brand = phone_dict["brand"]
        self.model = phone_dict["model"]
        self.storage = phone_dict["storage"]
        self.price = phone_dict["price"]
        self.timestamp = phone_dict["timestamp"]
        self.id = (self.brand, self.model, self.storage)
        
    def __repr__(self):
        return (f"{self.brand} {self.model} {self.storage}, "
                f"pris: {self.price}, scraped on {self.timestamp}")
    

class PhoneModel:
    scraped_dates = []
    
    def __init__(self, phone_data):
        self.id = phone_data.id
        self.phone_data = []
        self.is_active = None
        self.start_date = None
        self.end_date = None
        self.price_changes = []
    
    def add_phone(self, phone_data):
        self.phone_data.append(phone_data)
    
    def set_price_changes(self):
        for i in range(len(self.phone_data) - 1):
            t = self.phone_data[i + 1].timestamp
            delta = self.phone_data[i + 1].price - self.phone_data[i].price
            if delta != 0:
                self.price_changes.append({t: delta})
                #print(self.phone_data[i + 1], {t: delta}) 
    
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
    
    def finalise_model(self):
        self.set_price_changes()
        self.set_status_and_dates()
    
    def __repr__(self):
        return (f"{self.id}\n"
                f"start_date: {self.start_date}, \n"
                f"end_date: {self.end_date}\n")
    
with open(JSON_FILE, "r") as fp:
    phone_dicts = json.loads(fp.read())
    


filtered_phone_dicts = [pd for pd in phone_dicts if \
            datetime.datetime.strptime(pd["timestamp"], "%Y-%m-%d %H:%M:%S")\
            > START_DATE]

for phone_dict in filtered_phone_dicts:
    # Build list of all scraped datetimes
    PhoneModel.scraped_dates.append(
            datetime.datetime.strptime(phone_dict["timestamp"],
                                                  "%Y-%m-%d %H:%M:%S"))
    #Add phone_data to relevant model object if it exists. Otherwise create
    phone_data = PhoneData(phone_dict)
    if phone_data.id in phone_models:
        phone_models[phone_data.id].add_phone(phone_data)
    else:
        phone_model = PhoneModel(phone_data)
        phone_models[phone_data.id] = phone_model

for pm in phone_models.values():
    pm.finalise_model()
    print(pm)

