#!/usr/bin/env python3
#-*-conding: utf-8-*-

from functools import partial, wraps #偏函数
import inspect
import asyncio
import logging
from aiohttp import web

from apis import APIError

logging.basicConfig(level = logging.INFO)


def request(path, *, method):
	def decorator(func):
		@wraps(func)
		def warpper(*arg, **kw):
			return func(*arg, **kw)
		warpper.__route__ = path
		warpper.__method__ = method
		return warpper
	return decorator

get = partial(request, method = 'Get')
post = partial(request, method = 'Post')


#函数参数的获取并判断参数的种类
# 关于inspect.Parameter 的  kind 类型有5种：
# POSITIONAL_ONLY		只能是位置参数 （几乎用不到）
# POSITIONAL_OR_KEYWORD	可以是位置参数也可以是关键字参数
# VAR_POSITIONAL			相当于是 *args
# KEYWORD_ONLY			关键字参数且提供了key(命名关键字参数)
# VAR_KEYWORD			相当于是 **kw
#1、获取函数默认值为空的命名关键字参数（没有默认值所以参数一定要传，最后用于检查参数的缺失）
#2、获取命名关键字参数（在没有关键字参数时，不能传多余的参数，用于去除kw中多余的参数）
#3、判断函数是否有命名关键字参数
#4、判断函数是否有关键字参数
#5、判断函数是否有请求request参数（此处规定request参数必须写在POSITIONAL_OR_KEYWORD参数的最后一个）
'''
URL参数和GET、POST方法得到的参数彻底分离。

GET、POST方法的参数必需是KEYWORD_ONLY
URL参数是POSITIONAL_OR_KEYWORD
REQUEST参数要位于最后一个POSITIONAL_OR_KEYWORD之后的任何地方

@get('/{template}/')
async def home(template, *, tag='', page='1', size='10'):
    # 这里会传进去两个参数：template=bootstrap, tag=Refactoring
   pass
如果有request参数，它可以放在template之后的任何地方，没有看错，就是这么随便
def home(template, request, *, tag='', page='1', size='10'):
'''


#1、获取函数默认值为空的命名关键字参数（没有默认值所以参数一定要传，最后用于检查参数的缺失）
def get_required_kw_args(fn):
	args = []
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
			args.append(name)
	return tuple(args)


#2、获取命名关键字参数（在没有关键字参数时，不能传多余的参数（有命名关键字时可以多传参数），用于去除kw中多余的参数）
def get_all_kw_args(fn):
	args = []
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			args.append(name)
	return tuple(args)


#3、判断函数是否有命名关键字参数
def has_only_kw_args(fn):
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			return True


#4、判断函数是否有关键字参数
def has_var_kw_args(fn):
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.VAR_KEYWORD:
			return True 


#5、判断函数是否有请求request参数（此处规定request参数必须写在POSITIONAL_OR_KEYWORD参数的最后一个）
def has_request_arg(fn):
	sig = inspect.signature(fn)
	params = sig.parameters #raise ValueError using
	found = False
	for name, param in params.items():
		if name == 'request':
			found == True
			continue
		#当found为真，且下一个参数类型
		#Pay attention!!!
		if found and (param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_OR_KEYWORD)):
			raise ValueError('request parameter must be the last parameter in function:%s%s'%(fn__name__, str(sig)))
	return found


'''
RequestHandler流程（完全符合aiohttp框架要求）：
	1、从URL处理函数（handlers里面的一些函数）中分析需要接受的参数
	2、从web.request对象获取必要的参数，参数来源：
		网页中的GET和POST方法（比如获取/?page=10，还有json和from的数据），由data__factory函数实现
		request.match_info（比如获取@get('/api/{table}')装饰器里面的参数） __call__实现
		request参数(def __call__(self, request)传参)
	3、调用URL处理函数，将结果转化位web.Response对象
'''
class RequestHandler(object):
	def __init__(self, app, fn):
		self._app = app
		self._func = fn
		self._required_kw_args = get_required_kw_args(fn) #获取所有没有默认值的命名关键字参数
		self._all_kw_args = get_all_kw_args(fn) #获取所有的命名关键字参数
		self._has_only_kw = has_only_kw_args(fn) #是否有命名关键字参数
		self._has_var_kw = has_var_kw_args(fn) #是否有关键字参数
		self._has_request_kw = has_request_arg(fn) #是否有request参数 

	#RequestHandler 类由于定义了__call__()方法，因此可以将其实例视为一个函数
	async def __call__(self, request):
		#判断URL函数是否有参数
		logging.info('__call__')
		kw = None
		#
		if self._has_only_kw or self._has_var_kw:
			kw = getattr(request, '__data__', None)
		if kw is None:
			kw = dict(**request.match_info)
		else:
			#只有命名关键字时（不能多传参数），选出需要的参数
			if not self._has_var_kw and self._all_kw_args:
				copy = dict()
				for name in self._all_kw_args:
					if name in kw:
						copy[name] = kw[name]
				kw = copy
			for k, v in request.match_info.items():
				if k in kw:
					logging.warning('Duplicate arg name in named arg and kw args: %s'%k)
					kw[k] = v
		if self._has_request_kw:
			kw['request'] = request
		#检查参数是否有遗漏
		if self._required_kw_args:
			for name in self._required_kw_args:
				if not name in kw:
					return web.HTTPBadRequest()
		logging.info("call with args: %s"%str(kw))

		try:
			r = await self._func(**kw)
			return r
		except APIError as e:
			return dict(error = e.error, data = e.data, message = e.message)



def add_static(app):
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
	app.router.add_static('/static/', path)
	logging.info('add static %s => %s'%('/static/', path))


def add_route(app, fn):
	method = getattr(fn, "__method__", None)
	path = getattr(fn, "__route__", None)
	if method is None or path is None:
		raise ValueError("@get or @post not defined in %s"% str(fn))
	#Pay Attention!!!
	if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
		fn = asyncio.coroutine(fn)
	logging.info("add route %s %s => %s(%s)"%(method, path, fn.__name__, ','.join(inspect.signature(fn).parameters.keys())))
	app.router.add_route(method, path, RequestHandler(app, fn))
	#app.router.add_route(method, path, fn) 


def add_routes(app, module_name):
	n = module_name.rfind('.')
	#pay attention globals()\locals()
	if n == (-1):
		mod = __import__(module_name, globals(), locals())
	else:
		name = module_name[n+1:]
		mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
	for attr in dir(mod):
		if attr.startswith('_'):
			continue
		fn = getattr(mod, attr)
		if callable(fn):
			method = getattr(fn, '__method__', None)
			path = getattr(fn, '__route__', None)
			if method and path:
				add_route(app, fn)

def hello():
	pass
RequestHandler(1, hello)(1)