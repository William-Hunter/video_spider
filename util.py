#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import json
import time

def readJson(JSON_PATH):
    f = open(JSON_PATH, 'r', encoding='UTF-8')
    strr = f.read()
    f.close()
    return json.loads(strr)

def writeJson(JSON_PATH, obj):
    f = open(JSON_PATH, 'w', encoding='UTF-8')
    json.dump(obj, f, ensure_ascii=False, indent=2)
    f.close()


date_format = "%Y-%m-%d %H:%M:%S"

def date2stamp(dt):
    return time.mktime(time.strptime(dt, date_format))

def stamp2date(stamp):
    return time.strftime(date_format, time.localtime(stamp))
