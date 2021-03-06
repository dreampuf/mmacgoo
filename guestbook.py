#!/usr/bin/env python
#coding=utf-8
import cgi
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

import U115

class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')

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

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/sign', Guestbook),
  ('/ss', My),
  ('/u115', U115.U115),
  ('/u115/user', U115.U115UserControl),
  ('/u115/process', U115.U115Process)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
