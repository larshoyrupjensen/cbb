# -*- coding: utf-8 -*-
import json
import unicodedata

"""
Created on Sun Nov 19 19:04:08 2017

@author: Lars
"""

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
        json.dump(phones, fp, indent=4)

        
def normalise_unicode(text):
    if text is None:
        return text
    else:
        return unicodedata.normalize("NFKD", text)