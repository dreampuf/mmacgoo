#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Model
import Base
import Util
import json
import datetime, time
import re
import random
import logging
import xml.sax.saxutils as saxutils
from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

#### Model Area ####
import mimetypes
import mimetools

class U115User(Model.BaseModel):
    ''' U115 User Model '''
    username = db.StringProperty()
    password = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    lastopt = db.DateTimeProperty()

    def delete(self):
        Base.Cache.delete("U115UserList")
        super(U115User, self).delete()

    @classmethod
    def delbyname(cls, username):
        Base.Cache.delete("U115UserList")
        u = db.Query(cls).gql("WHERE username=:1", username).get()
        if not u:
            pass
        logs = db.Query(U115Log).gql("WHERE by=:1", u.key()).fetch(1000)
        db.delete(logs)
        db.delete(u)

    @classmethod
    def exists(cls, username):
        return (U115User.gql("WHERE username=:1", username).count() > 0)

    @classmethod
    def add(cls, username, password):
        Base.Cache.delete("U115UserList")
        u = U115User(username=username,password=password,lastopt=datetime.datetime.now()-datetime.timedelta(hours=5))
        u.put()
        return u

    @classmethod
    def modify(cls, key, username, password, lastopt):
        Base.Cache.delete("U115UserList")
        u = U115User.get(key)
        u.username = username
        u.password = password
        u.lastopt = lastopt
        u.put()
        return u

    @classmethod
    def all(cls, limit=10, offset=0):
        curall = Base.Cache.get("U115UserList")
        if curall == None:
            query = db.Query(U115User)
            query.order("-created")
            curall = query.fetch(limit, offset)
            Base.Cache.set("U115UserList", curall)
        return curall

class U115Log(Model.BaseModel):
    '''U115 Log Model'''
    by = db.ReferenceProperty(U115User)
    content = db.StringProperty(multiline=True)
    time = db.DateTimeProperty(auto_now_add=True)
    type = db.StringProperty()

    _count = None
    @classmethod
    def all(cls, limit=10, offset=0):
        query = db.Query(cls)
        query.order("-time")
        return query.fetch(limit, offset)

    @classmethod
    def count(cls):
        if cls._count == None:
            cls._count = db.Query(cls).count(None)
        return cls._count

### Model Area End ###

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = str(time.time())
    CRLF = '\r\n'
    L = []
    for key in fields.keys():
        value = fields[key]
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


class U115(Base.BaseWebRequest):
    def get(self):
        postdata = {
                    "login[account]" : "soddyque@163.com",
                    "login[passwd]" : "111111"
                }

        hp = Util.HttpHelper()
        response = hp.open(url="http://my.115.com/?action=login&goto=http%3A%2F%2Fu.115.com%2F%3Fac%3Dmy",
                           method=Util.HttpHelper.POST,
                           postdata=postdata)
        response = hp.open(url="http://u.115.com/?ac=my")
        upfileKey = re.findall("setPostParams\({aid:a.aid,cid:a.cid,cookie:\"(.+?)\"}\)", response.content)
        if len(upfileKey) > 0:
            upfileKey = upfileKey[0]
        else:
            upfileKey = ""
            pass

        fileds = {"Filename" : "Filename",
                   "aid" : "2",
                   "cookie" : upfileKey,
                   "Upload" : "Submit Query"}
        wenjian = u"abcdefgO"
        files = [("Filedata",
                         u"cc%s.txt" % (random.randint(1000, 9999) ,),
                         ''.join(random.sample(wenjian, len(wenjian))))]


        content_type, body = encode_multipart_formdata(fileds, files)
        headers = {'Content-Type': content_type,}
                   #'Content-Length': str(len(body))} #GEA Con't Modified
        response = hp.open(url="http://u.115.com/index.php?ctl=upload&action=temp_upload",
                           method = Util.HttpHelper.POST,
                           postdata = body,
                           headers = headers)
        rObj = json.read(response.content)
        if rObj["state"]:
            self.response.out.write("True")
        else:
            self.response.out.write("False")

    def post(self):
        psss

class U115UserControl(Base.BaseWebRequest):
    def get(self):
        out = self.response.out

        ###Delete User###
        du = self.request.get("d")
        if du:
            U115User.delbyname(du)
            self.redirect("/u115/user")

        out.write("Has These User In System:<br /><ul>")
        list = U115User.all()
        for i in list:
            out.write("<li>%s</li>" % i.username)
        out.write("</ul>")

        out.write("""
        <form action="user" method="post">
        UserName : <input name="username" type="text" /><br />
        Password : <input name="password" type="password" /><br />
        <input type="submit" value="Post" />
        </form>
        """)

    def post(self):
        out = self.response.out
        username = self.request.get("username")
        password = self.request.get("password")

        if not U115User.exists(username) :
            u = U115User.add(username, password)

        self.redirect("")

class U115Process(Base.BaseWebRequest):
    @classmethod
    def UserCookie(cls, value=None):
        if value:
            Base.Cache.set("U115UserCookie", value)
        uc = Base.Cache.get("U115UserCookie")
        if uc == None:
            uc = {}
            Base.Cache.set("U115UserCookie", uc)
        return uc

    def get(self):
        out = self.response.out
        uc = U115Process.UserCookie()
        hp = Util.HttpHelper()

        action = self.request.get("action")
        if action == "upfile": #UpFile Module ###############
            ukey = self.request.get("u")
            cur = U115User.get(ukey)
            ccookie = uc[cur.username]
            hp.set_cookie(ccookie)
            response = hp.open(url="http://u.115.com/?ac=my")
            upfileKey = re.findall("setPostParams\({aid:a.aid,cid:a.cid,cookie:\"(.+?)\"}\)", response.content)

            if len(upfileKey) > 0:
                upfileKey = upfileKey[0]
            else:
                upfileKey = ""
                return

            fileds = {"Filename" : "Filename",
                       "aid" : "2",
                       "cookie" : upfileKey,
                       "Upload" : "Submit Query"}
            wenjian = u"abcdefgO"
            files = [("Filedata",
                             u"cc%s.txt" % (random.randint(1000, 9999) ,),
                             ''.join(random.sample(wenjian, len(wenjian))))]

            content_type, body = encode_multipart_formdata(fileds, files)
            headers = {'Content-Type': content_type} #'Content-Length': str(len(body))
            logging.info(u"HasUPFile")
            for i in range(4):
                try:
                    response = hp.open(url="http://u.115.com/index.php?ctl=upload&action=temp_upload",
                                       method = Util.HttpHelper.POST,
                                       postdata = body,
                                       headers = headers)
                    rObj = json.read(response.content)
                    if rObj["state"]:
                        logging.info(u"%s上传了文件" % cur.username)
##                        log = U115Log()
##                        log.by = cur.key()
##                        log.type = "info"
##                        log.content = u"%s上传了文件" % (cur.username ,)
##                        log.put()
                except Exception, e:
                    logging.debug("An Error: % s" %e)
            return

        elif action == "receiveaward" : #Receive Award Space ################
            ukey = self.request.get("u")
            cur = U115User.get(ukey)
            ccookie = uc[cur.username]
            hp.set_cookie(ccookie)
            response = hp.open("http://u.115.com/?ct=ajax&ac=pick_storage")
            if response.content != "no":
                #{"picked":"10MB","total_size":"3082MB","used_percent":"0%"}
                r = json.read(response.content)
                out.write(r)
                #r = json.read('{"picked":"10MB","total_size":"3082MB","used_percent":"0%"}')
                log = U115Log()
                log.by = cur.key()
                log.type = "info"
                log.content = u"领取到了%s空间, 总共有%s" % (r["picked"], r["total_size"])
                log.put()
            return

        elif action == "login" : #Login
            ukey = self.request.get("u")
            cur = U115User.get(ukey)

            postdata = {
                "login[account]" : cur.username,
                "login[passwd]" : cur.password
            }
            response = hp.open(url="http://my.115.com/?action=login&goto=http%3A%2F%2Fu.115.com%2F%3Fac%3Dmy",
                                       method=Util.HttpHelper.POST,
                                       postdata=postdata)
            if response.content.find("用户名不存在或密码输入错误") != -1:
                log = U115Log()
                log.by = cur.key()
                log.type = "info"
                log.content = u"用户名不存在或密码输入错误"
                log.put()
            logging.info("%s" % cur.username)
            uc[cur.username] = hp.cookie
            logging.info(u"has Loging")
            U115Process.UserCookie(uc)
            return

        curlist = U115User.all(1000, 0)
        for cur in curlist:
            #用户登录
            taskqueue.add(url="/u115/process?action=login&u=%s" % cur.key(), method="GET")
            diff = cur.lastopt + datetime.timedelta(hours=4)  < datetime.datetime.utcnow()
            if diff:
            #if True:
                cur.lastopt = datetime.datetime.utcnow()
                cur.put()
                Base.Cache.delete("U115UserList")
                #领取奖励空间
                taskqueue.add(url="/u115/process?action=receiveaward&u=%s" % cur.key(), method="GET")

                #上传文件
                taskqueue.add(url="/u115/process?action=upfile&u=%s" % cur.key(), method="GET")

            #FOR END








class U115LogDetail(Base.BaseWebRequest):
    def get(self):
        out = self.response.out
        limit = int(self.request.get("limit", "10"))
        p = int(self.request.get("p", "1"))
        p = 1 if p == 0 else p
        list = U115Log.all(limit, p)
        total = U115Log.count()

        out.write(u"""
        <table><tr><td>来自</td><td>时间</td><td>类型</td><td>内容</td></tr><tbody>
        """)
        for i in list:
            out.write(u"""<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" %
                      (i.by.username, i.time, i.type, i.content))
        out.write("""
        </tbody></table><br />
        """)
        out.write("%s<br />"%total)
        prehref = 'href="?limit=%s&p=%s"' % (limit, p-1) if p > 1 else ''
        nexthref = 'href="?limit=%s&p=%s"' % (limit, p+1) if p*limit < total else ''
        out.write("""
        <a %s>pre</a>|<a %s>next</a>
        """ % (prehref, nexthref))

    def post(self):
        pass