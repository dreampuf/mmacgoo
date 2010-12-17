#! /usr/bin/env python
#coding=utf-8

import datetime
from google.appengine.ext import webapp
from google.appengine.api import memcache

class BaseWebRequest(webapp.RequestHandler):
    '''Base Web Request Class'''
    pass


class Cache:
    @classmethod
    def get(cls, key):
        return memcache.get(key)

    @classmethod
    def set(cls, key, value, time=0):
        memcache.set(key, value, time)

    @classmethod
    def delete(cls, key, seconds=0):
        memcache.delete(key, seconds)

    @classmethod
    def incr(cls, key, delta=1):
        memcache.incr(key, delta)

    @classmethod
    def decr(cls, key, delta=1):
        memcache.decr(key, delta)

    @classmethod
    def flush_all(cls):
        memcache.flush_all()

    @classmethod
    def get_stats(cls):
        return memcache.get_stats()


ZERO_TIME_DELTA = datetime.timedelta(0)
class LocalTimezone(datetime.tzinfo):
	def utcoffset(self, dt):
		return datetime.timedelta(hours=8)

	def dst(self, dt):
		return ZERO_TIME_DELTA

LOCAL_TIMEZONE = LocalTimezone()

class UTC(datetime.tzinfo):
	def utcoffset(self, dt):
		return ZERO_TIME_DELTA

	def dst(self, dt):
		return ZERO_TIME_DELTA
UTC = UTC()

def ParserTime(dtstr, format = "%Y/%m/%d %H:%M:%S"):
    return datetime.datetime.strptime(dtstr, format)

def ParserLocalTimeToUTC(dtstr, format = "%Y/%m/%d %H:%M:%S"):
    return ParserTime(dtstr, format).replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC)

def LocalToUTC(dt):
    if dt.tzinfo:
        dt.replace(tzinfo=None)
    return dt.replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC)

def UTCtoLocal(dt):
    if dt.tzinfo:
        dt.replace(tzinfo=None)
    return dt.replace(tzinfo=UTC).astimezone(LOCAL_TIMEZONE)