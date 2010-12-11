#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi, sys
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

reload(sys)
sys.setdefaultencoding("utf-8")
import U115
import Mail

class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><title>Hello</title><body>')

    greetings = db.GqlQuery("SELECT * "
                            "FROM Greeting "
                            "ORDER BY date DESC LIMIT 10")

    for greeting in greetings:
      if greeting.author:
        self.response.out.write('<b>%s</b> wrote:' % greeting.author.nickname())
      else:
        self.response.out.write('An anonymous person wrote:')
      self.response.out.write('<blockquote>%s</blockquote>' %
                              cgi.escape(greeting.content))

    self.response.out.write("""
          <form action="/sign" method="post">
            <div><textarea name="content" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Sign Guestbook"></div>
          </form>
        </body>
      </html>""")


class Guestbook(webapp.RequestHandler):
  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/')


class My(webapp.RequestHandler):
    def post(self):
        pass
    def get(self):
        from google.appengine.api import urlfetch
        from BeautifulSoup import BeautifulSoup
        from BSXPath import BSXPathEvaluator,XPathResult
        result = urlfetch.fetch(url="http://www.u17.com/comic_list/le!_th99_gr99_ca99_ss99_ob0_m0_p1.html",
                                headers={'dd': 'dd'})
        if(result.status_code == 200):
            doc = BSXPathEvaluator(result.content)#/OL[20]/DIV[1]/A[1]/IMG[1]
            r = doc.getFirstItem('/html[1]/BODY[1]/DIV[8]/DIV[3]/DIV[2]/DIV[12]')
            self.response.out.write(r)
            #soup = BeautifulSoup(result.content)
            #listZimu = soup.find('div', attrs={'class':'new_zimu'})
            #for i in listZimu.findAll('a'):
            #    self.response.out.write(i.text + ':' + i['href'] + '<br />')
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
class TaskTest(webapp.RequestHandler):

    def get(self):
        '''
        q = self.request.get("q")
        if len(q):
            for i in range(int(q)):
                taskqueue.add(url="/t", queue_name="default")
            return

        out = self.response.out
        t = memcache.get("t")
        if t == None:
            t = 0
            memcache.set("t", t)

        out.write("The t is : %s" % t)
        '''
        q = memcache.get("t")
        if q == None:
            q = [{'a':1,'b':'d'}, 1, "a"]
            memcache.set("t", q)
            self.response.out.write("has update")
        else:
            self.response.out.write(q[0]['a'])

    def post(self):
        t = memcache.get("t")
        if t == None:
            t = 0
            memcache.set("t", t)
        else:
            memcache.incr("t")

class PyV(webapp.RequestHandler):
    def get(self):
        import PyV8
        ctxt = PyV8.JSEngine()
        ctxt.enter()
        r = ctxt.eval("1+2")
        self.request.out.write(r)

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/sign', Guestbook),
  ('/ss', My),
  ('/v', PyV),
  ('/mail', Mail.MailSender),
  ('/mail/view', Mail.MailControl),
  ('/u115', U115.U115),
  ('/u115/user', U115.U115UserControl),
  ('/u115/log', U115.U115LogDetail),
  ('/u115/process', U115.U115Process),
  Mail.MailReceive.mapping()
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
