import hashlib
import json
import redis

from storage import Store

class RedisStore(Store):
    def __init__(self, db_host):
        self.db = redis.StrictRedis(db_host)

    def put(self, payload):
        payload_str = json.dumps(payload, default=lambda s: str(s)).encode('utf-8')
        key = hashlib.sha1(payload_str).hexdigest()
        self.db.set(key, payload_str, ex=86400)
        return key
    
    def get(self, key):
        response = self.db.get(key)
        if response:
            self.db.delete(key)
            response = json.loads(response)
        return response

