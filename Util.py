#! /usr/bin/env python
#coding=utf-8

import urllib, Cookie,logging
from google.appengine.api import urlfetch

class HttpHelper(object):
    UserAgent = "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3"
    GET = 1
    POST = 2
    HEAD = 3
    PUT = 4
    DELETE = 5
    def __init__(self,
                 headers={},
                 cookie=None,
                 useragent=None):
        self.headers = headers
        if cookie:
            if isinstance(cookie, basestring):
                 self.__cookie = Cookie.SimpleCookie(cookie)
            else:
                self.__cookie = cookie
        else:
            self.__cookie = Cookie.SimpleCookie()

        if useragent:
            self.useragent = useragent
        else:
            self.useragent = HttpHelper.UserAgent

    @classmethod
    def _make_cookie_header(cls, cookie):
        ret = ""
        for val in cookie.values():
            ret+="%s=%s; "%(val.key, val.value)
        return ret

    def open(self, url, cookie=None, postdata=None, useragent=None,method=urlfetch.GET, headers={}):
        if cookie :
            self.__cookie.load(cookie)
        if useragent:
            self.useragent = useragent
        if postdata and not isinstance(postdata, basestring):
            postdata = urllib.urlencode(postdata)

        _headers = {"cookie": HttpHelper._make_cookie_header(self.__cookie),
                    "User-Agent":self.useragent}
        _headers.update(headers)
        curi = 0
        curmax = 5
        while url is not None:
            if(curi >= curmax):
                break
            try:
               curi += 1
               response = urlfetch.fetch(url=url,
                                    method=method,
                                    payload=postdata,
                                    headers=_headers,
                                    allow_truncated=False,
                                    follow_redirects=False,
                                    deadline=10
                                    )
               postdata = None
               self.__cookie.load(response.headers.get('set-cookie', ''))
               _headers.update({"cookie" : HttpHelper._make_cookie_header(self.__cookie)})
               url = response.headers.get('location')
            except Exception, e:
               logging.error("%s" % (logging.traceback.extract_stack()))

        return response

    @property
    def cookie(self):
        return self.__cookie.output()[11:]
    def set_cookie(self, value):
        if isinstance(value, basestring):
            self.__cookie = Cookie.SimpleCookie(value)
        else:
            self.__cookie = Cookie.SimpleCookie()


