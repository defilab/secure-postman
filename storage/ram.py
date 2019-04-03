import hashlib
import json

from storage import Store

class RamStore(Store):
    def __init__(self):
        self.store = dict()

    def put(self, payload):
        key = hashlib.sha1(json.dumps(payload, default=lambda s: str(s)).encode('utf-8')).hexdigest()
        self.store[key] = payload
        return key
    
    def get(self, key):
        response = self.store.get(key)
        if response:
            del self.store[key]
        return response

