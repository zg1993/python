#!/usr/bin/env python
#-*- coding: utf-8-*-

from tornado import gen
@gen.coroutine
def divide(x, y):
	return x / y

def bad_call():
	divide(1, 0)

@gen.coroutine
def good_call():
	yield divide(1, 0)

import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Hello, world")

def make_app():
	return tornado.web.Application([
		(r"/", MainHandler),
		])

# if __name__ == "__main__":
# 	app = make_app()
# 	app.listen(8888)
# 	tornado.ioloop.IOLoop.current().start()


import pdb 
import socket
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

# 1传统方法
# url = '/'
# sock = socket.socket()
# sock.connect(('xkcd.com', 80))
# print(sock)
# request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(url)
# encoded = request.encode('ascii')
# response = b''
# sock.send(encoded)
# chunk = sock.recv(4096)
# while chunk:
# 	response += chunk
# 	chunk = sock.recv(4096)
# print(response)

# 2异步
# url = '/'
# sock = socket.socket()
# sock.setblocking(False)
# print(sock)
# # 即使非阻塞套接字工作正常，它也会抛出错误
# try:
# 	sock.connect(('xkcd.com', 80))
# except BlockingIOError:
# 	pass
# request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(url)
# encoded = request.encode('ascii')
# # 这个循环会一直遍历直到套接字准备好，缺点浪费电并且不能高效的处理多个套接字，
# # 所以我们使用I/O多路复用的select来监视多个socket
# while True:
# 	try:
# 		sock.send(encoded)
# 		# 只有当套接字准备好了才会跳出循环
# 		break
# 	# 套接字没准备好时抛出 OSError
# 	except OSError as e:
# 		pass

# 3使用select 这里实现了异步框架的两个特性：非阻塞和事件循环
# from selectors import DefaultSelector, EVENT_WRITE

# selector = DefaultSelector()
# url = '/'
# sock = socket.socket()
# sock.setblocking(False)
# print(sock)
# # 即使非阻塞套接字工作正常，它也会抛出错误
# try:
# 	sock.connect(('xkcd.com', 80))
# except BlockingIOError:
# 	pass
# request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(url)
# encoded = request.encode('ascii')

# def connected():
# 	print(sock)
# 	#pdb.set_trace()
# 	# 可以把 selector 看作一个存储套接字的容器，一旦容器里面没有套接字，抛出 OSError 错误
# 	selector.unregister(sock.fileno())
# 	print('connected')
# 	sock.send(encoded)
# print(sock)
# selector.register(sock.fileno(), EVENT_WRITE, connected)

# def loop():
# 	while True:
# 		try:
# 			events = selector.select()
# 		# selector 里的套接字都被注销了
# 		except OSError as e:
# 			break
# 		for event_key, event_mask in events:
# 			callback = event_key.data
# 			callback()

# loop()
#chunk = sock.recv(4096)


# # 4Fetcher类
# urls_todo = set(['/']) # 代办事宜
# seen_urls = set(['/']) # 已经爬取的url
# selector = DefaultSelector()

# # 5
# class Future:
# 	def __init__(self):
# 		self.result = None
# 		self._callbacks = []

# 	def add_done_callback(self, fn):
# 		self._callbacks.append(fn)

# 	def set_result(self, result):
# 		self.result = result
# 		for fn in self._callbacks:
# 			fn(self)
# # num_step = 0
# class Task:
# 	def __init__(self, coro):
# 		self.coro = coro
# 		f = Future()
# 		f.set_result(None)
# 		self.step(f)

# 	def step(self, future):
# 		# nonlocal num_step
# 		# num_step += 1
# 		# print(num_step)
# 		try:
# 			next_future = self.coro.send(future.result)
# 		except StopIteration:
# 			return
# 		next_future.add_done_callback(self.step)

# class Fetcher:
# 	# Fetcher 对象三个属性： url, socket, response
# 	def __init__(self, url):
# 		self.response = b''
# 		self.url = url
# 		self.sock = None

# 	# fetch方法开始连接一个套接字，它返回在这个连接被建立之前
# 	# def fetch(self):
# 	# 	self.sock = socket.socket()
# 	# 	self.sock.setblocking(False)
# 	# 	try:
# 	# 		self.sock.connect(('xkcd.com', 80))
# 	# 	except BlockingIOError:
# 	# 		pass
# 	# 	# 注册回调函数
# 	# 	selector.register(self.sock.fileno(),
# 	# 					  EVENT_WRITE,
# 	# 					  self.connected)

# 	# 5升级版的fetch方法，使用生成器
# 	def fetch(self):
# 		sock = socket.socket()
# 		sock.setblocking(False)
# 		try:
# 			sock.connect(('xkcd.com', 80))
# 		except BlockingIOError:
# 			pass
		
# 		f = Future()

# 		def on_connected():
# 			f.set_result(None)

# 		selector.register(sock.fileno(),
# 						 EVENT_WRITE,
# 						 on_connected)
# 		print('before yield {}'.format(sock))
# 		yield f
# 		print('after yield {}'.format(sock))
# 		selector.unregister(sock.fileno())
# 		print('connected')

# 	# callback函数，当socket写准备好时调用
# 	def connected(self, key, mask):
# 		print('connected')
# 		selector.unregister(key.fd)
# 		request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(self.url)
# 		self.sock.send(request.encode('ascii'))
# 		# 注册下一个回调函数 表示可读EVENT_READ
# 		selector.register(key.fd,
# 						  EVENT_READ,
# 						  self.read_response)

# 	# callback函数， 当socket读准备好时调用
# 	def read_response(self, key, mask):
# 		global stopped
# 		chunk = self.sock.recv(4096) # 4k 大小
# 		if chunk:
# 			self.response += chunk
# 		else:
# 			selector.unregister(key.fd) # 读取完毕
# 			print('url: {} read content{}'.format(self.url, self.response))

# stopped = False
# def loop():
# 	while not stopped:
# 		try:
# 			events = selector.select()
# 		except IOError:
# 			print('error')
# 			break
# 		for event_key, event_mask in events:
# 			callback = event_key.data
# 			callback()

# fetcher = Fetcher('/353/')
# Task(fetcher.fetch())
# loop()


# 生成器测试
# def gen_fn():
# 	print(111)
# 	result = yield 1
# 	print('result yield {}'.format(result))
# 	result2 = yield 2
# 	print('result2 yield {}'.format(result2))
# 	return 'done'

# a = gen_fn()
# a.send(None)
# print(a.send(None))
# print(a)























