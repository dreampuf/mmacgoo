#! /usr/bin/env python
#coding=utf-8

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