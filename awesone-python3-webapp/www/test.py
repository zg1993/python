import orm
from models import User
from config import configs
import asyncio, aiomysql

async def test(loop):
	await orm.create_pool(loop = loop, **configs.db)
	#u = User(id = '1', name = 'zg')
	#f = await User.find(pk = 1)
	u = User(name='Test', email='tet1@example.com', passwd='1234567890', image='about:blank')
	await u.save()
	#print('type(f): %s f: %s'%(type(f), f))

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()

