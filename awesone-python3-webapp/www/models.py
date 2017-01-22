#!/usr/bin/env python3
#-*-conding: utf-8-*-


import uuid, time

from orm import Model, StringField, FloatField, TextField, BooleanField



#generate ID
def next_id():
	return '%015d%s000'%(int(time.time() * 1000), uuid.uuid4().hex)



class User(Model):
	__table__ = 'users'

 
	id = StringField(primary_key = True, default = next_id, ddl = 'varchar(50)') #在getValueOrDefault()中使用 
	email = StringField(ddl = 'varchar(50)')
	passwd = StringField(ddl = 'varchar(50)') #默认的ddl位‘varchar(100)’
	admin = BooleanField()
	name = StringField(ddl = 'varchar(50)')
	image = StringField(ddl = 'varchar(500)')
	created_at = FloatField(default = time.time)

	def __init__(self, **kw):
		super(User, self).__init__(**kw)



class Blog(Model):
	__table__ = 'blogs'

	id = StringField(primary_key = True, default = next_id, ddl = 'varchar(50)') #在getValueOrDefault()中使用 
	user_id = StringField(ddl = 'varchar(50)')
	user_name = StringField(ddl = 'varchar(50)')
	user_image = StringField(ddl = 'varchar(500)')
	name = StringField(ddl = 'varchar(50)')
	summary = StringField(ddl = 'varchar(200)')
	content = TextField()
	created_at = FloatField(default = time.time)

	def __init__(self, **kw):
		super(Blog, self).__init__(**kw)



class Comment(Model):
	__table__ = 'comments'


	id = StringField(primary_key = True, default = next_id, ddl = 'varchar(50)') #在getValueOrDefault()中使用 
	blog_id = StringField(ddl = 'varchar(50)')
	user_id = StringField(ddl = 'varchar(50)')
	user_name = StringField(ddl = 'varchar(50)')
	user_image = StringField(ddl = 'varchar(500)')
	content = TextField()
	created_at = FloatField(default = time.time)

	def __init__(self, **kw):
		super(Comment, self).__init__(**kw)


















