#!/usr/bin/env python3
"""
🔴 MASTER BRAIN - Central Orchestrator
Routes: internal vs external
Enforces policies
Manages access
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any
try:
    import jwt
except:
    jwt = None

class UserType(Enum):
    INTERNAL = "internal"  # Company employees
    EXTERNAL = "external"  # Customers

class MasterBrain:
    """Central decision-making engine"""
    
    def __init__(self):
        self.secret_key = "your-secure-key-here"  # Use env vars!
        self.internal_brain_url = "http://localhost:5010"
        self.external_brain_url = "http://localhost:5011"
        self.routing_log = []
    
    def authenticate_user(self, token: str) -> Dict[str, Any]:
        """Decode & verify JWT token"""
        if not jwt:
            return {'valid': False, 'error': 'JWT not available'}
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return {
                'valid': True,
                'user_id': payload.get('user_id'),
                'user_type': UserType(payload.get('user_type', 'external')),
                'tenant_id': payload.get('tenant_id'),
                'roles': payload.get('roles', [])
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def route_request(self, user_auth: Dict, request_data: Dict) -> Dict:
        """
        CORE ROUTING LOGIC
        IF internal ��� INTERNAL BRAIN
        ELSE → EXTERNAL BRAIN
        """
        
        routing_decision = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_auth.get('user_id'),
            'user_type': user_auth.get('user_type').value if user_auth.get('user_type') else 'unknown',
            'request': request_data.get('action'),
            'decision': None,
            'target_brain': None,
            'allowed': False,
            'reason': ''
        }
        
        # 1. Check user type
        if user_auth.get('user_type') == UserType.INTERNAL:
            # Internal users have access to INTERNAL BRAIN
            routing_decision['target_brain'] = 'internal'
            routing_decision['allowed'] = self.check_internal_policy(user_auth, request_data)
            
            if not routing_decision['allowed']:
                routing_decision['reason'] = 'Permission denied for internal action'
        
        else:  # EXTERNAL
            # External users route to EXTERNAL BRAIN
            routing_decision['target_brain'] = 'external'
            routing_decision['allowed'] = self.check_external_policy(user_auth, request_data)
            
            if not routing_decision['allowed']:
                routing_decision['reason'] = 'Permission denied for external action'
        
        # Log routing decision
        self.routing_log.append(routing_decision)
        
        return routing_decision
    
    def check_internal_policy(self, user_auth: Dict, request: Dict) -> bool:
        """Policy enforcement for INTERNAL users"""
        
        required_roles = {
            'server_access': ['admin', 'devops'],
            'deploy': ['admin', 'devops', 'lead'],
            'security_audit': ['admin', 'security'],
            'view_logs': ['admin', 'devops']
        }
        
        action = request.get('action')
        user_roles = set(user_auth.get('roles', []))
        
        if action in required_roles:
            return any(r in user_roles for r in required_roles[action])
        
        return False
    
    def check_external_policy(self, user_auth: Dict, request: Dict) -> bool:
        """Policy enforcement for EXTERNAL users (Customers)"""
        
        tenant_id = user_auth.get('tenant_id')
        request_tenant = request.get('tenant_id')
        
        # Can only access own tenant
        if tenant_id != request_tenant:
            return False
        
        # Block dangerous actions
        dangerous_actions = [
            'server_access',
            'deploy_to_production',
            'view_system_logs',
            'modify_security'
        ]
        
        if request.get('action') in dangerous_actions:
            return False
        
        return True
    
    def execute_request(self, routing_decision: Dict, request_data: Dict) -> Dict:
        """Execute request through appropriate brain"""
        
        if not routing_decision['allowed']:
            return {
                'status': 'denied',
                'error': routing_decision['reason']
            }
        
        target = routing_decision['target_brain']
        
        if target == 'internal':
            return self.call_internal_brain(request_data)
        else:
            return self.call_external_brain(request_data)
    
    def call_internal_brain(self, request: Dict) -> Dict:
        """Call INTERNAL BRAIN (high privilege)"""
        return {
            'status': 'routed_to_internal',
            'request': request,
            'timestamp': datetime.now().isoformat()
        }
    
    def call_external_brain(self, request: Dict) -> Dict:
        """Call EXTERNAL BRAIN (customer-safe)"""
        return {
            'status': 'routed_to_external',
            'request': request,
            'timestamp': datetime.now().isoformat()
        }
    
    def process(self, token: str, request_data: Dict) -> Dict:
        """MAIN PROCESS"""
        
        # Authenticate
        user_auth = self.authenticate_user(token)
        if not user_auth['valid']:
            return {'error': 'Unauthorized', 'status': 401}
        
        # Route
        routing = self.route_request(user_auth, request_data)
        
        # Execute
        result = self.execute_request(routing, request_data)
        
        return {
            'result': result,
            'routing': routing,
            'timestamp': datetime.now().isoformat()
        }

