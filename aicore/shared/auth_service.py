#!/usr/bin/env python3
"""
JWT-based authentication
Role-based access control
"""

import jwt
import json
from datetime import datetime, timedelta
from typing import Dict
from enum import Enum

class AuthService:
    """Handle authentication & tokens"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self, user_id: str, user_type: str, tenant_id: str, roles: list) -> str:
        """Generate JWT token"""
        
        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'tenant_id': tenant_id,
            'roles': roles,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Dict:
        """Verify and decode token"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except:
            return {'valid': False}

