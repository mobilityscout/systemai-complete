#!/usr/bin/env python3
"""
Shared caching with ISOLATION
Internal vs External namespaces
"""

import redis
import json
from typing import Any

class CacheLayer:
    """Redis cache with tenant isolation"""
    
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    def get_key(self, user_type: str, tenant_id: str, key: str) -> str:
        """Generate namespace-prefixed key"""
        return f"{user_type}:{tenant_id}:{key}"
    
    def set(self, user_type: str, tenant_id: str, key: str, value: Any, ttl: int = 3600):
        """Set value with namespace"""
        full_key = self.get_key(user_type, tenant_id, key)
        self.redis.setex(full_key, ttl, json.dumps(value))
    
    def get(self, user_type: str, tenant_id: str, key: str) -> Any:
        """Get value with namespace"""
        full_key = self.get_key(user_type, tenant_id, key)
        value = self.redis.get(full_key)
        return json.loads(value) if value else None
    
    def delete(self, user_type: str, tenant_id: str, key: str):
        """Delete with namespace"""
        full_key = self.get_key(user_type, tenant_id, key)
        self.redis.delete(full_key)

