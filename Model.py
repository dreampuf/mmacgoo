#! /usr/bin/env python
#coding=utf-8
import pickle
from google.appengine.ext import db
from google.appengine.ext.db import Model as DBModel

class BaseModel(db.Model):
	def __init__(self, parent=None, key_name=None, _app=None, **kwds):
		self.__isdirty = False
		DBModel.__init__(self, parent=None, key_name=None, _app=None, **kwds)

	def __setattr__(self,attrname,value):
		"""
		DataStore api stores all prop values say "email" is stored in "_email" so
		we intercept the set attribute, see if it has changed, then check for an
		onchanged method for that property to call
		"""
		if (attrname.find('_') != 0):
			if hasattr(self,'_' + attrname):
				curval = getattr(self,'_' + attrname)
				if curval != value:
					self.__isdirty = True
					if hasattr(self,attrname + '_onchange'):
						getattr(self,attrname + '_onchange')(curval,value)

		DBModel.__setattr__(self,attrname,value)


class OptionSet(BaseModel):
	name=db.StringProperty()
	value=db.TextProperty()
	#blobValue=db.BlobProperty()
	#isBlob=db.BooleanProperty()

	@classmethod
	def getValue(cls,name,default=None):
		try:
			opt=OptionSet.get_by_key_name(name)
			return pickle.loads(str(opt.value))
		except:
			return default

	@classmethod
	def setValue(cls,name,value):
		opt=OptionSet.get_or_insert(name, name=name)
		opt.name=name
		opt.value=pickle.dumps(value)
		opt.put()

		return value

	@classmethod
	def remove(cls,name):
		opt= OptionSet.get_by_key_name(name)
		if opt:
			opt.delete()

class Mail(BaseModel):
	sender = db.StringProperty()
	to = db.StringProperty()
	reply_to = db.StringProperty()
	subject = db.StringProperty()
	body = db.TextProperty()
	html = db.TextProperty()
	time = db.DateTimeProperty(auto_now=True)

	@classmethod
	def add(cls, sender, to, reply_to, subject, body, html):
		m = Mail(sender=sender,
				 to=to,
				 reply_to=reply_to,
				 subject=subject,
				 body=db.Text(body),
				 html=db.Text(html))
		m.put()
		return m

	@classmethod
	def all(cls, limit=10, offset=0):
	    query = db.Query(cls)
	    query.order("-time")
	    return query.fetch(limit, offset)

	@classmethod
	def get(cls, key):
		return db.get(key)

class MailAttachment(BaseModel):
	filename = db.StringProperty()
	data = db.BlobProperty()
	by = db.ReferenceProperty(Mail, collection_name="attachments")

	@classmethod
	def add(cls, by, filename, data):
		ma = MailAttachment(filename=filename, data=db.Blob(data), by=by)
		ma.put()
		return ma

	@classmethod
	def get(cls, key):
		return db.get(key)