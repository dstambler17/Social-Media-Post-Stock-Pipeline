import redis

class RedisClient():
    def __init__(self, host='localhost', port=6379, db=0, password=None, socket_timeout=None):
        self._client = redis.Redis(host=host, port=port, db=0, password=None)
    
    def write(self, key, value):
        self._client.mset({key: value})
    
    def read(self, key):
        return self._client.get(key)
    
    def read_dict(self, key):
        return self._client.hgetall(key)
    
    def write_dict(self, key, value):
        self._client.hmset(key, value)
