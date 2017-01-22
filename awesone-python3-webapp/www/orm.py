import asyncio, aiomysql
import functools 
import logging



logging.basicConfig(level = logging.INFO)#打印logging.info()的内容注释后不显示

#标记运行到哪个函数
def mylog(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        #print(func.__name__, 'begin')
        print(func.__qualname__, 'begin')
        #print(dir(func), 'begin')
        r = func(*args, **kw)
        print(func.__qualname__, 'end')
        return r
    return wrapper



#创建连接池，方便每个http请求都可以从连接池中直接获取数据库连接
@mylog
async def create_pool(loop, **kw):
	logging.info('create database connection pool...')
	global __pool
	__pool = await aiomysql.create_pool(
		#host = kw.get('host', 'localhost'), #key中没有host时返回默认value：localhost
		#port = kw.get('port', 3500),#mysql的的端口
		user = kw['user'],#登录的用户名
		password = kw['password'],
		db = kw['database'],#打开数据库名称
		charset = kw.get('charset', 'utf8'),#pay attention!!! 'not utf-8'
		autocommit =kw.get('autocommit', True),#自动提交模式，默认为False
		maxsize = kw.get('maxsize', 10), #最大连接数
		minsize = kw.get('minsize', 1),
		loop = loop
	)
	logging.info("__pool: %s"%__pool)



#mysql查找
@mylog
async def select(sql, args, size = None):
	#print(sql, args)
	global __pool
	#从连接池中获取数据库连接
	async with  __pool.get() as conn: # with...as 自动执行conn.close()
		try:
			cur = await conn.cursor(aiomysql.DictCursor)
			await cur.execute(sql.replace('?', '%s'), args or ()) #args为None的时候取'()'
			#如果指定了size大小打印相应数量的查询信息，否则打印全部
			if size:
				rs = await cur.fetchmany(size)
			else:
				rs = await cur.fetchall() #接收全部的返回结果
			await cur.close() #关闭cur
		except BaseException as e:
			raise
		finally:
			conn.close()
		logging.info('rows return: %s type(rs): %s rs: %s'%(len(rs), type(rs), rs))
		return rs



#Insert, Update, Delete
#mysql 插入 修改 删除 这三个sql语句的执行需要相同的参数，cur对象都是通过rowcout返回结果数
@mylog
async def execute(sql, args):
	#logging.info(sql, args)
	async with __pool.get() as conn:
		try:
			cur = await conn.cursor(aiomysql.DictCursor)
			#print(sql.replace('?', '%s'), args)
			await cur.execute(sql.replace('?', '%s'), args)
			#await cur.execute("insert into users (name, id) values (%s, %s)", ('zg11', '1'))
			affected = cur.rowcount #这是一个只读属性，并返回执行execute()方法后影响的行数
			logging.info('affected: %s'%affected)
			#print('`users`')
			#await conn.commit() #提交事务（已设置为自动提交模式）
			await cur.close()
		except BaseException as e:#sql语句可能不合法，抛出错误
			raise
		finally:
			conn.close()
		return affected



#ORM 对象-映射关系 （一个类对应一个表） 通过元类来实现
#编写ORM框架
#第一步，先把调用接口写出来。比如，使用者如果使用这个ORM框架，想定义一个User类来操作对应的数据库表User，我们期待他写出这样的代码：
# class User(Model):
#     __table__ = 'users'
# id为属性名 StringField里的string类型（尚未确定）才是mysql里的名字
#     id = IntegerField(primary_key=True)
#     name = StringField()
#     ...

# # 创建实例:
# user = User(id=123, name='Michael',...)
# 存入数据库:
# user.save()
# 查询所有User对象:
# users = User.findAll()
#其中Model和属性类StringField、IntegerField由ORM框架提供
#save()、findAll()等方法由metaclass自动完成

class Field(object):
	#初始化参数包括属性（列）名，属性（列）的类型，是否有主键
	#default 待定？？default参数用于赋初值时没有给出值的属性使用
	#如：一个User的属于有id name password 构造User(name = 'zg', password = '**')
	#此时id没有给出，使用default去取得，具体实现在getValueOrDefault()函数中
	
	def __init__(self, name, column_type, primary_key, default):
		self.name = name
		self.column_type = column_type
		self.primary_key = primary_key
		self.default = default

	def __str__(self):
		return '<%s, %s: %s>'%(self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
	# ddl(data definition languages)：用于定义数据类型
	def __init__(self, name = None, primary_key = False, default = None, ddl = 'varchar(100)'):
		#super(StringField,self).__init__(name, ddl, primary_key, default)
		super().__init__(name, ddl, primary_key, default)


#不能成为主键
class BooleanField(Field):
	def __init__(self, name = None, default = False):
		super(BooleanField, self).__init__(name, 'boolean', False, default)


class IntegerField(Field):
	def __init__(self, name = None, primary_key = False, default = 0):
		super().__init__(name, 'bigint', primary_key, default)
		#super(IntegerField, self).__init__(name, 'bigint', primary_key, default)


class FloatField(Field):
	def __init__(self, name = None, primary_key = False, default = 0.0):
		super(FloatField, self).__init__(name, 'real', primary_key, default)


#不能成为主键
class TextField(Field):
	def __init__(self, name = None, default = None):
		super(TextField, self).__init__(name, 'text', False, default)


# 构造占位符
def create_placeholder(num):
	if not isinstance(num, int):
		raise TypeError('bad type')
	l = []
	for n in range(num):
		l.append('?')
	return ','.join(l)



#创建元类
class ModelMetaclass(type):
	@mylog
	def __new__(cls, name, bases, attrs):
		#排除对Model类的修改
		#Modele的子类创建时也会隐式的继承metaclass(也是通过元类创建)
		if name == 'Model':
			return type.__new__(cls, name, bases, attrs)
		logging.info('create class %s to ModelMetaclass' %name)
		tableName = attrs.get('__table__', None) or name
		logging.info('tableName: %s' %tableName)
		#获取所有的field和主键名
		mappings = dict() #保存类和属性的映射关系
		fields = [] #除主键外的属性名
		primaryKey = None #主键属性名
		for k, v in attrs.items():
			if isinstance(v, Field):
				mappings[k] = v
			#if getattr(v, 'primary_key', None):	modify
				if v.primary_key:
					if primaryKey:
						raise RuntimeError('Duplicate primary key for field: %s'% k)
					primaryKey = k
				else:
					fields.append(k)
		if not primaryKey:
			raise RuntimeError(' primary key not found')
		#在类属型中删除mappings中对应的属性
		for k in mappings.keys():
			attrs.pop(k)
		#map返回一个Iterator（迭代器：可以被next()函数调用并不断返回下个值的对象）
		escaped_fields = list(map(lambda f: "`%s`"%f, fields))
		attrs['__mappings__'] = mappings #属性和列的关系
		attrs['__fields__'] = fields #除主键属性外的属性名
		attrs['__primary_key__'] = primaryKey #主键属性名
		attrs['__table__'] = tableName #表名
		#构造SELECT, INSERT, UPDATE和DELETE语句
		attrs['__select__'] = "select `%s`, %s from `%s`"%(primaryKey, ','.join(escaped_fields), tableName)
		attrs['__insert__'] = "insert into `%s` (%s, `%s`) values (%s)"%(tableName, ','.join(escaped_fields), primaryKey, create_placeholder(len(escaped_fields)+1))
		#attrs['__update__'] = "update '%s' set %s where '%s'=?"%(tableName, ','.join(map(lambda f:"'%s'=?"%(getattr(mappings.get(f), 'name', None) or f), fields)), primaryKey)
		attrs['__update__'] = "update `%s` set %s where `%s`=?"%(tableName, ','.join(map(lambda f:"'%s'=?"%(mappings.get(f).name or f), fields)), primaryKey)
		#attrs['__update__'] = 'update `%s` set %s where `%s` = ?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
		attrs['__delete__'] = "delete from `%s` where `%s`=?"%(tableName, primaryKey)
		return type.__new__(cls, name, bases, attrs)



class Model(dict, metaclass = ModelMetaclass):

	def __init__(self, **kw):
		super(Model, self).__init__(**kw)

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Model'object has no attribute'%s'"%key)

	def getValue(self, key):
		return getattr(self, key, None)

	def getValueOrDefault(self, key):
		value = getattr(self, key, None)
		if value is None:
			#field是一个为赋初值的对象
			field = self.__mappings__[key] #是一个Field子类的对象，比如FloatField(default = time.time)
			print(123, field)
			if field.default is not None:
				#callable 判断field.default是否是实例方法
				#FloatField field.default = time.time 所以它是一个可调用的对象调用形式为field.default()
				#BooleanField field.default 默认为False 调用方法为 field.default

				value = field.default() if callable(field.default) else field.default
				logging.info('using default value for %s: %s'%(key, str(value)))
				setattr(self, key, value)
		return value


	#根据键值查找
	#??用法
	@classmethod
	@mylog
	async def find(cls, pk):
		#print(pk)
		rs = await select("%s where `%s`=?"%(cls.__select__, cls.__primary_key__), [pk], 1)
		logging.info('rs of type: %s'%type(rs))
		if len(rs) == 0:
			return None
		#print(type(rs[0]))
		#cls继承自dict
		return cls(**rs[0])


	@mylog
	async def save(self):
		args = list(map(self.getValueOrDefault, self.__fields__))
		args.append(self.getValueOrDefault(self.__primary_key__))
		logging.info(self.__insert__)
		rows = await execute(self.__insert__, args)
		logging.info('rows of type: %s'%type(rows))
		if rows != 1:
			logging.warn("failed to insert record")


	@classmethod
	@mylog
	async def findAll(cls, where = None, args = None, **kw):
		sql = [cls.__select__]
		if where:
			sql.append('where')
			sql.append(args)
		if args is None:
			args = []
		orderBy = kw.get('orderBy', None)
		if orderBy:
			sql.append('order by')
			sql.append(orderBy)
		limit = kw.get('limit', None)
		if limit is not None:
			sql.append('limit')
			if isinstance(limit, int):
				sql.append('?')
				args.append(limit)
			elif isinstance(limit, tuple) and len(limit) == 2:
				sql.append('?,?')
				args.extend(limit)
			else:
				raise ValueError('Invalid limit value: %s'%str(limit))
		rs = await select(''.join(sql), args)
		return [cls(**r) for r in rs]

	@classmethod
	@mylog
	async def findNum(cls, selectField, where = None, args = None):
		sql = ['select %s _num_ from `%s`'%(selectField, cls.__table__)]
		if where:
			sql.append('where')
			sql.append(where)
		print(sql)
		rs = await select(' '.join(sql), args, 2) 
		print(rs, type(rs))
		if len(rs) == 0:
			return None
		return rs[0]['_num_']

'''
# test code 
class User(Model):
    __table__ = 'users'
#id为属性名 StringField里的string类型（尚未确定）才是mysql里的名字
    #id = IntegerField(primary_key=True)
    id = StringField(primary_key=True)
    name = StringField()

    def __init__(self, **kw):
    	super(User, self).__init__(**kw)

from config import configs

async def test(loop):
	await create_pool(loop = loop, **configs.db)
	#u = User(id = '1', name = 'zg')
	#f = await User.find(pk = 1)
	u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')

	print('type(f): %s f: %s'%(type(f), f))

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
#'''