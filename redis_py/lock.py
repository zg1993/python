LOCK_EXPIRE = 10

'''
    redis command: setnx, getset
'''
@gen.coroutine
def acquire_lock(lockname, acquire_timeout=5):
    enter_timestamp = time.time()
    while time.time() - enter_timestamp > 5:
        timestamp = time.time()
        if lasting_redis.setnx(lockname, timestamp + LOCK_EXPIRE):
            raise gen.Return(timestamp + LOCK_EXPIRE)
        else:
            last_timestamp = lasting_redis.get(lockname)
            if timestamp - last_timestamp > LOCK_EXPIRE:
                old_timestamp = lasting_redis.getset(lockname, timestamp + LOCK_EXPIRE)
                if old_timestamp == last_timestamp:
                    raise gen.Return(timestamp + LOCK_EXPIRE)
                else:
                    yield gen.sleep(0.01)
            else:
                yield gen.sleep(0.01)
    raise gen.Return(False)
