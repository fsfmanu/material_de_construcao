'''
import redis
import json

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)

    def set_conversation_context(self, session_id, context, expiration_seconds=3600):
        self.client.setex(f"conversation:{session_id}", expiration_seconds, json.dumps(context))

    def get_conversation_context(self, session_id):
        context = self.client.get(f"conversation:{session_id}")
        return json.loads(context) if context else None

redis_manager = RedisManager()
'''
