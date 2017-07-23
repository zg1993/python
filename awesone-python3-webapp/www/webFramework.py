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



# 向app中添加静态文件目录
def add_static(app):
    # os.path.abspath(__file__), 返回当前脚本的绝对路径(包括文件名)
    # os.path.dirname(), 去掉文件名,返回目录路径
    # os.path.join(), 将分离的各部分组合成一个路径名
    # 因此以下操作就是将本文件同目录下的static目录(即www/static/)加入到应用的路由管理器中
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    # app = web.Application(loop=loop)这是在app.py模块中定义的
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))

# 把请求处理函数注册到app
# 处理将针对http method 和path进行
# 下面的add_routes函数的一部分
def add_route(app, fn):
    method = getattr(fn, '__method__', None)  # 获取fn.__method__属性,若不存在将返回None
    path = getattr(fn, '__route__', None)  # 获取fn.__route__属性,若不存在将返回None
    if path is None or method is None:  # 如果两个属性其中之一没有值，那就会报错
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    # 如果函数fn是不是一个协程或者生成器，就把这个函数编程协程
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))  # 注册request handler

   
# 将handlers模块中所有请求处理函数提取出来交给add_route自动去处理
def add_routes(app, module_name):
    # 如果handlers模块在当前目录下，传入的module_name就是handlers
    # 如果handlers模块在handler目录下没那传入的module_name就是handler.handlers

    # Python rfind() 返回字符串最后一次出现的位置，如果没有匹配项则返回-1。
    # str.rfind(str, beg=0 end=len(string))
    # str -- 查找的字符串
    # beg -- 开始查找的位置，默认为0
    # end -- 结束查找位置，默认为字符串的长度。
    # 返回字符串最后一次出现的位置(索引数），如果没有匹配项则返回-1。
    n = module_name.rfind('.')
    if n == (-1):
        # __import__(module_name[, globals[, locals[, fromlist]]]) 可选参数默认为globals(),locals(),[]
        # 例如>>> mod = __import__("test", globals(), locals())
        #     >>> mod
        #     <module 'test' from 'C:\\Users\\shabi\\test.py'>
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]  # 当module_name为handler.handlers时，[n+1:]就是取.后面的部分，也就是handlers
        # 下面的语句相当于执行了两个步骤，传入的module_name是aaa.bbb
        # 第一个步骤获取aaa模块的信息
        # 第二个步骤通过getattr()方法取得子模块名, 如aaa.bbb
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    # dir()不带参数时，返回当前范围内的变量、方法和定义的类型列表；带参数时，返回参数的属性、方法列表。如果参数包含方法__dir__()，该方法将被调用。如果参数不包含__dir__()，该方法将最大限度地收集参数信息。
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        # 排除私有属性之后，用getattr调用handlers模块离得里的属性（方法）
        # fn就是handler里的函数
        fn = getattr(mod, attr)
        if callable(fn):  # 查看提取出来的属性是不是函数
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            # 如果是函数，再判断是否有__method__和__route__属性，如果存在则使用app_route函数注册
            if method and path:
                add_route(app, fn)

def hello():
	pass
RequestHandler(1, hello)(1)