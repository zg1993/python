#!/usr/bin/env python3
#-*-conding: utf-8-*-

from functools import partial #偏函数
import inspect


def request(path, *, method):
	def decorator(func):
		@functools.warps(func)
		def warpper(*arg, **kw):
			return func(*arg, **kw)
		warpper.__rout__ = path
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
# KEYWORD_ONLY			关键字参数且提供了key
# VAR_KEYWORD			相当于是 **kw
#1、获取函数默认值为空的命名关键字参数（没有默认值所以参数一定要传，最后用于检查参数的缺失）
#2、获取命名关键字参数（在没有关键字参数时，不能传多余的参数（有命名关键字时可以多传参数），用于去除kw中多余的参数）
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
		if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
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
		if request.__data__ is None:
			print(11)
			pass




def add_route(app, fn):
	pass

RequestHandler(2,add_route)(request)