# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 19:04:08 2017

@author: Lars
"""
loaded=[{'brand': 'Huawei', 'storage': '32 GB', 'model': 'P10 Lite', 'price': 799, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Samsung', 'storage': '64 GB', 'model': 'Galaxy S8+', 'price': 5599, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Nokia', 'storage': '64 GB', 'model': '8', 'price': 3299, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Samsung', 'storage': '32 GB', 'model': 'Galaxy S7 Edge', 'price': 4499, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Huawei', 'storage': '16 GB', 'model': 'P9 Lite ', 'price': 1499, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Sony', 'storage': '64 GB', 'model': 'Xperia XZ1', 'price': 4499, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Samsung', 'storage': '32 GB', 'model': 'Galaxy S7', 'price': 3699, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Huawei', 'storage': '16 GB', 'model': 'P8 Lite', 'price': 999, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Sony', 'storage': '16 GB', 'model': 'Xperia XA', 'price': 1896, 'timestamp': '2017-11-18 20:41:02'}, {'brand': 'Sony', 'storage': '64 GB', 'model': 'Xperia XZ1', 'price': 4499, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Sony', 'storage': '16 GB', 'model': 'Xperia XA', 'price': 1896, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Huawei', 'storage': '32 GB', 'model': 'P10 Lite', 'price': 799, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Samsung', 'storage': '64 GB', 'model': 'Galaxy S8+', 'price': 5599, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Samsung', 'storage': '32 GB', 'model': 'Galaxy S7', 'price': 3699, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Samsung', 'storage': '32 GB', 'model': 'Galaxy S7 Edge', 'price': 4499, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Huawei', 'storage': '16 GB', 'model': 'P9 Lite ', 'price': 1499, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Nokia', 'storage': '64 GB', 'model': '8', 'price': 3299, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Huawei', 'storage': '16 GB', 'model': 'P8 Lite', 'price': 999, 'timestamp': '2017-11-18 20:43:01'}, {'brand': 'Huawei', 'storage': '16 GB', 'model': 'P8 Lite', 'price': 999, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Nokia', 'storage': '64 GB', 'model': '8', 'price': 3299, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Samsung', 'storage': '64 GB', 'model': 'Galaxy S8+', 'price': 5599, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Huawei', 'storage': '16 GB', 'model': 'P9 Lite ', 'price': 1499, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Sony', 'storage': '64 GB', 'model': 'Xperia XZ1', 'price': 4499, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Huawei', 'storage': '32 GB', 'model': 'P10 Lite', 'price': 799, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Sony', 'storage': '16 GB', 'model': 'Xperia XA', 'price': 1896, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Samsung', 'storage': '32 GB', 'model': 'Galaxy S7 Edge', 'price': 4499, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Samsung', 'storage': '32 GB', 'model': 'Galaxy S7', 'price': 3699, 'timestamp': '2017-11-19 14:15:14'}, {'brand': 'Nokia', 'storage': '64 GB', 'model': '8', 'price': 3299, 'timestamp': '2017-11-19 18:58:59'}, {'brand': 'Sony', 'storage': '16 GB', 'model': 'Xperia XA', 'price': 1896, 'timestamp': '2017-11-19 18:58:59'}, {'brand': 'Samsung', 'storage': '32 GB', 'model': 'Galaxy S7 Edge', 'price': 4499, 'timestamp': '2017-11-19 18:58:59'}, {'brand': 'Huawei', 'storage': '16 GB', 'model': 'P9 Lite ', 'price': 1499, 'timestamp': '2017-11-19 18:58:59'}, {'brand': 'Samsung', 'storage': '64 GB', 'model': 'Galaxy S8+', 'price': 5599, 'timestamp': '2017-11-19 18:58:59'}, {'brand': 'Sony', 'storage': '64 GB', 'model': 'Xperia XZ1', 'price': 4499, 'timestamp': '2017-11-19 18:58:59'}, {'brand': 'Samsung', 'storage': '32 GB', 'model': 'Galaxy S7', 'price': 3699, 'timestamp': '2017-11-19 18:58:59'}, {'brand': 'Huawei', 'storage': '32 GB', 'model': 'P10 Lite', 'price': 799, 'timestamp': '2017-11-19 18:58:59'}, {'brand': 'Huawei', 'storage': '16 GB', 'model': 'P8 Lite', 'price': 999, 'timestamp': '2017-11-19 18:58:59'}]
new=[{'brand': 'Huawei',
  'model': 'P10 Lite',
  'price': 799,
  'storage': '32 GB',
  'timestamp': '2019-11-18 08:41:02'},
 {'brand': 'Samsung',
  'model': 'Galaxy S8+',
  'price': 5599,
  'storage': '64 GB',
  'timestamp': '2019-11-18 08:41:02'},
 {'brand': 'Nokia',
  'model': '8',
  'price': 3299,
  'storage': '64 GB',
  'timestamp': '2019-11-18 08:41:02'},
 {'brand': 'Samsung',
  'model': 'Galaxy S7 Edge',
  'price': 4499,
  'storage': '32 GB',
  'timestamp': '2019-11-18 08:41:02'},
 {'brand': 'Huawei',
  'model': 'P9 Lite ',
  'price': 1499,
  'storage': '16 GB',
  'timestamp': '2019-11-18 08:41:02'},
 {'brand': 'Sony',
  'model': 'Xperia XZ1',
  'price': 4499,
  'storage': '64 GB',
  'timestamp': '2019-11-18 08:41:02'},
 {'brand': 'Samsung',
  'model': 'Galaxy S7',
  'price': 3699,
  'storage': '32 GB',
  'timestamp': '2019-11-18 08:41:02'},
 {'brand': 'Huawei',
  'model': 'P8 Lite',
  'price': 699,
  'storage': '16 GB',
  'timestamp': '2019-11-18 08:41:02'},
 {'brand': 'Sony',
  'model': 'Xperia XA',
  'price': 1696,
  'storage': '16 GB',
  'timestamp': '2019-11-18 08:41:02'}]


def find_changed_phones(new_phones, all_phones):
    changed_phones_since_last_run=[]
    for n in new_phones:
        old_versions=[p for p in all_phones if
                      p["brand"]==n["brand"] and
                      p["model"]==n["model"] and
                      p["storage"]==n["storage"]]
        #If n is phone that has never been scraped before there are no old
        #versions and we should continue to next new phone
        if old_versions == []:
            continue
        old_sorted=sorted(old_versions, 
                          key=lambda k: k["timestamp"], 
                          reverse=True)
        #print("NEW", n)
        #print("OLD SORTED", old_sorted)
        #If new phones have been saved to all phones, pick next newest as
        #comparison phone. Should not be necessary
        if n["timestamp"]==old_sorted[0]["timestamp"]:
            next_newest=old_sorted[-1]
        else:
            next_newest=old_sorted[0]
        #Check if price has changed
        try:
            delta=n["price"]-next_newest["price"]
        except TypeError:
            delta = 0
        if delta != 0:
            n["delta"]=delta
            n["old_price"]=next_newest["price"]
            changed_phones_since_last_run.append(n)
    return changed_phones_since_last_run
            
        