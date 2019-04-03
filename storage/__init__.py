class Store(object):
    def put(self, payload):
        raise NotImplementedError()

    def get(self, key):
        raise NotImplementedError()

from storage.ram import RamStore
from storage.redis import RedisStore
