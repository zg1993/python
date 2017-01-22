#!/usr/bin/env python3
#_*_ coding:utf-8 _*_

__author__ = 'zg'


'async web application.'

#实现异步IO，实现单线程并发IO操作
#asyncio的编程模型就是一个消息循环。我们从asyncio模块中直接获取一个EventLoop的引用
#然后把需要执行的协程扔到EventLoop中执行，就实现了异步IO。
import asyncio
#aiohttp则是基于asyncio实现的HTTP框架
from aiohttp import web
import time
from urllib import parse
import logging

logging.basicConfig(level = logging.INFO)#打印logging.info()的内容注释后不显示


#middleware拦截器
async def logger_factory(app, handler):
	async def logger_fact(request):
		logging.info('Request: %s %s'%(request.method, request.path))
		return (await handler(request))
	return logger_fact
#async def auth_factory(app, handler):
#网页中的GET和POST方法（比如获取/?page=10，还有json或form的数据
#GET和POST数据的获取
#brief 把GET和POST的数据绑定在request.__data__上
async def data_factory(app, handler):
		async def parse_data(request):

				if request.method == 'POST':
					if not request.content_type:
						return web.HTTPBadRequest(text = 'Miss Content_Type')
					ct = request.content_type.lower()
					if ct.startswith('application/json'):
						params = await request.json()
						if not isinstance(params, dict):
							return web.HTTPBadRequest(text = 'JSON body must be object')
					elif ct.startswith(('application/x-www-form-urlencoded', 'application/form-data')):
						params = await request.post()
						request.__data__ = dict(**params)
					else:
						return web.HTTPBadRequest(text = 'Unsupported Content_Type: %s'%request.content_type)

				elif request.method == 'GET': 
					qs = request.query_string
					if qs:
						request.__data__ = {k: v[0] for k, v in parse.prase_qs(qs, True).items()}

				else:
					request.__data__ = dict()

		return parse_data



logging.basicConfig(level = logging.INFO)
# logging.basicConfig(level = logging.INFO,
# 	format = '%(asctime)s %(filename)s[line: %(lineno)d] %(levelname)s %(message)s',
# 	datefmt = '%a, %d %b %Y %H:%H:%S',
# 	filename = 'myapp.log',
# 	filemode = 'w')
async def index(request):
	body = '<h1>Awe微软sone</h1>'
	print(1,request,2)
	#print(dir(request))
	print(request.content_type)
	print(request.content_type.lower())
	print(1,request.method,2)
	print(3,request.match_info)
	print(2,request.query_string,3)
	#模拟文件IO操作
	await asyncio.sleep(1)
	return web.Response(body = body.encode('utf-8'), content_type = 'text/html')



async def hello(request):
	print(2,request.query_string,3, type(request.query_string))

	print(3,request.match_info)
	print('json', request.json())
	print('post', request.post())
	print(3, request.match_info)
	print(4, dir(request.match_info))

	print(5, type(request.match_info))
	#print(4,request.match_info['keys'])
	await asyncio.sleep(1)
	return web.Response(body = '<h1>hello</h1>'.encode('utf-8'), content_type = 'text/html')



#async将一个generator标记为coroutine类型??
async def init(loop):
	app = web.Application(loop = loop)
	app.router.add_route('GET', '/A', index)
	app.router.add_route('GET', '/hello/{name}', hello)
	srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
	logging.info('server started at http://127.0.0.1:8000...')
	return srv



#获取EventLoop
loop = asyncio.get_event_loop()#loop是一个消息循环对象
#把coroutine扔到EventLoop中执行
loop.run_until_complete(init(loop))#在消息循环中执行协程
loop.run_forever()


