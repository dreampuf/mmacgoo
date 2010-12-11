import logging
import xml.sax.saxutils as saxutils

from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 

import Base, Model

class MailReceive(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        
        sender = mail_message.sender
        to = mail_message.to
        #reply_to = mail_message.reply_to
        reply_to = ""
        subject = mail_message.subject
        if not hasattr(mail_message, "body"):
            body = ""
        elif isinstance(mail_message.body, mail.EncodedPayload):
            body = mail_message.body.decode()
        else:
            body = mail_message.body
        if not hasattr(mail_message, "html"):
            html = ""
        elif isinstance(mail_message.html, mail.EncodedPayload):
            html = mail_message.html.decode()
        else:
            html = mail_message.html
        
        m = Model.Mail.add(sender, to, reply_to, subject, body, html)
        if hasattr(mail_message, "attachments"):
            for filename, data in mail_message.attachments:
                data = isinstance(data, mail.EncodedPayload) and data.decode() or data
                a = Model.MailAttachment.add(m, filename, data)
        
class MailControl(Base.BaseWebRequest):
    def get(self):
        out = self.response.out
        isOneView = self.request.get("k")
        isBlodView = self.request.get("f")
        
        if isBlodView:
            ablod = Model.MailAttachment.get(isBlodView)
            houzui = ('.' in ablod.filename) and ablod.filename.rsplit('.',1)[1] or ablod.filename
            self.response.headers["Content-Type"] = mail.EXTENSION_MIME_MAP[houzui]
            out.write(ablod.data)
            
        elif isOneView:
            imail = Model.Mail.get(isOneView)
            attachments = ""
            for iattach in imail.attachments:
                attachments += """<li><a href="/mail/view?f=%s">%s</a></li>""" % (iattach.key(), iattach.filename)
            out.write(u"""<div>
            sender:%s <br />
            to:%s <br />   
            subject:%s <br />
            ===============body===================<br />
            %s
            <br />
            ===============html===================<br />
            %s
            <br />
            ===============attachments============<br />
            <ul>
            %s
            </ul>
            </div>""" % (saxutils.escape(imail.sender), saxutils.escape(imail.to), imail.subject, imail.body, imail.html, attachments))
            
        else:
            out.write("<ul>")
            list = Model.Mail.all()
            for i in list:
                out.write(u"""
                <li><a href="/mail/view?k=%s">%s</a></li>
                """ % (i.key(), saxutils.escape(i.sender)))
                
            out.write("</ul>")

class MailSender(Base.BaseWebRequest):
    def get(self):
        out = self.response.out
        
        out.write(u"""<form method="POST"> 
        <label for="from">从</lable><input type="text" name="from" value="xxx" />@mmacgoo.appspotmail.com<br /> 
        <label for="to">发送到</lable><input type="text" name="to" /><br /> 
        <label for="title">标题</lable><input type="text" name="title" /><br /> 
        <label for="content">内容</lable><textarea style="margin-left: 2px; margin-right: 2px; width: 556px; " rows="10" name="content" ></textarea><br /> 
        <input type="submit" value="提交" /> 
        </form>""")
    
    def post(self):
        out = self.response.out
        
        fr = self.request.get("from")
        fr = fr and (fr + "@mmacgoo.appspotmail.com") or "admin@mmacgoo.appspotmail.com"
        to = self.request.get("to")
        title = self.request.get("title")
        content = self.request.get("content")
        
        mail_msg = mail.EmailMessage(sender=fr, to=to,subject=title, body=content)
        
        try:
            mail_msg.send()
        except:
            logging.info(u"发送邮件错误.%s到%s.标题:%s" % (fr, to, title))
        
        self.redirect("")
    