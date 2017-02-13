

import asyncio
from webFramework import get, post

from models import User
from aiohttp import web
import logging
logging.basicConfig(level = logging.INFO)

@get('/')
async def index(request):
	logging.info('index')
	users = await User.findAll()
	return {
		'__template__': 'test.html',
		'users': users
	}

# @get('/')
# async def index(request):
# 	body = '<h1>Awe微软sone</h1>'
# 	return  web.Response(body = body.encode('utf-8'), content_type = 'text/html')