#!/usr/bin/env python3
"""
CHAT ASSISTANT - Die Intelligenz hinter dem Master Brain
Versteht natürlich, routet intelligent, lernt kontinuierlich
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
import uuid

class ConversationContext:
    """Speichert Conversation History pro Session"""
    
    def __init__(self, user_id: str, tenant_id: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.messages = []
        self.context_data = {}
        self.detected_intent = None
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to history"""
        self.messages.append({
            'timestamp': datetime.now().isoformat(),
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'metadata': metadata or {}
        })
    
    def get_context(self) -> Dict:
        """Get full context for analysis"""
        return {
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'message_count': len(self.messages),
            'last_messages': self.messages[-5:],  # Last 5 messages
            'context_data': self.context_data
        }


class IntentDetector:
    """Erkennt was User WIRKLICH will"""
    
    @staticmethod
    def detect(user_input: str, context: Dict) -> Dict:
        """Detektiere Intent aus Input"""
        
        text_lower = user_input.lower()
        
        intents = {
            # Development intents
            'code_generation': {
                'keywords': ['code', 'schreib', 'generier', 'funktion', 'class', 'write'],
                'needs_copilot': True,
                'requires_external': False
            },
            'code_review': {
                'keywords': ['review', 'überprüf', 'feedback', 'kritik', 'besser'],
                'needs_copilot': True,
                'requires_external': False
            },
            'pull_request': {
                'keywords': ['pull request', 'pr', 'merge', 'commit', 'push'],
                'needs_git': True,
                'requires_external': False
            },
            'issue_tracking': {
                'keywords': ['issue', 'bug', 'problem', 'feature', 'task'],
                'needs_github': True,
                'requires_external': False
            },
            
            # Infrastructure intents
            'server_status': {
                'keywords': ['server', 'status', 'läuft', 'online', 'health'],
                'needs_infra': True,
                'requires_internal': True
            },
            'deployment': {
                'keywords': ['deploy', 'push', 'release', 'production'],
                'needs_deploy': True,
                'requires_internal': True
            },
            'monitoring': {
                'keywords': ['monitor', 'logs', 'error', 'metric', 'performance'],
                'needs_monitor': True,
                'requires_internal': True
            },
            
            # Business intents
            'app_building': {
                'keywords': ['app', 'anwendung', 'bauen', 'builder', 'application'],
                'needs_builder': True,
                'requires_external': True
            },
            'workflow': {
                'keywords': ['workflow', 'automation', 'process', 'ablauf'],
                'needs_workflow': True,
                'requires_external': True
            },
            'api_design': {
                'keywords': ['api', 'endpoint', 'rest', 'graphql'],
                'needs_api_builder': True,
                'requires_external': True
            },
            
            # Relationship
            'small_talk': {
                'keywords': ['wie geht', 'danke', 'hallo', 'hi', 'like', 'love'],
                'is_relationship': True
            }
        }
        
        detected = []
        requirements = {
            'needs_internal': False,
            'needs_external': False,
            'capabilities': []
        }
        
        for intent_name, config in intents.items():
            if any(kw in text_lower for kw in config.get('keywords', [])):
                detected.append(intent_name)
                
                if config.get('requires_internal'):
                    requirements['needs_internal'] = True
                if config.get('requires_external'):
                    requirements['needs_external'] = True
                
                # Sammle benötigte Fähigkeiten
                for key, val in config.items():
                    if key.startswith('needs_') and val:
                        requirements['capabilities'].append(key.replace('needs_', ''))
        
        return {
            'intents': detected if detected else ['general_query'],
            'requirements': requirements,
            'confidence': 0.8 if detected else 0.5
        }


class ResponseGenerator:
    """Generiert natürliche, intelligente Responses"""
    
    @staticmethod
    def generate(user_input: str, intent_result: Dict, user_type: str, context: Dict) -> Dict:
        """Generiere Response basierend auf Intent"""
        
        response = {
            'content': '',
            'action': None,
            'route_to_brain': None,
            'confidence': intent_result['confidence']
        }
        
        intents = intent_result['intents']
        
        # SMALL TALK - antworte sofort
        if 'small_talk' in intents:
            responses = [
                "Mir geht's gut! 😊 Womit kann ich dir helfen?",
                "Danke der Nachfrage! Was beschäftigt dich gerade?",
                "Schön, dich zu treffen! Erzähl mir von dir.",
            ]
            response['content'] = responses[0]
            return response
        
        # CODE GENERATION - nutze Copilot-ähnliche Features
        if 'code_generation' in intents:
            response['content'] = f"Verstanden! Ich schreibe dir den Code. Was genau brauchst du?\n\nGib mir:\n1. Was soll die Funktion tun?\n2. Welche Inputs/Outputs?\n3. Welche Sprache?"
            response['action'] = 'code_generation'
            response['route_to_brain'] = 'external' if user_type == 'external' else 'internal'
            return response
        
        # PULL REQUEST - Git Integration
        if 'pull_request' in intents:
            response['content'] = "Ich erstelle einen PR für dich. Details:\n- Welcher Branch?\n- Welche Commits/Changes?\n- PR Title & Description?"
            response['action'] = 'create_pr'
            response['route_to_brain'] = 'internal'
            return response
        
        # SERVER STATUS - nur Internal
        if 'server_status' in intents:
            if user_type != 'internal':
                response['content'] = "Das ist nur für interne Teams verfügbar. 🔐"
                return response
            response['content'] = "Analysiere Server Status... (brauche Admin Access)"
            response['action'] = 'analyze_server'
            response['route_to_brain'] = 'internal'
            return response
        
        # DEPLOYMENT - nur Internal
        if 'deployment' in intents:
            if user_type != 'internal':
                response['content'] = "Deployments sind nur für das interne Team möglich."
                return response
            response['content'] = "Deployment vorbereitet. Welche App/Service?"
            response['action'] = 'deploy'
            response['route_to_brain'] = 'internal'
            return response
        
        # APP BUILDING - nur External
        if 'app_building' in intents:
            response['content'] = "Großartig! Ich baue dir eine App. Was soll sie können?\n- Chat-App?\n- Business-Tool?\n- API?"
            response['action'] = 'build_app'
            response['route_to_brain'] = 'external'
            return response
        
        # Default
        response['content'] = "Interessant! Erzähl mir mehr - was genau brauchst du?"
        response['action'] = 'general_query'
        
        return response


class ChatAssistant:
    """Hauptmotor - kombiniert alles"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}
        self.intent_detector = IntentDetector()
        self.response_generator = ResponseGenerator()
    
    def get_or_create_session(self, user_id: str, tenant_id: str) -> ConversationContext:
        """Get existing session or create new one"""
        session_key = f"{user_id}:{tenant_id}"
        
        if session_key not in self.sessions:
            self.sessions[session_key] = ConversationContext(user_id, tenant_id)
        
        return self.sessions[session_key]
    
    def process(self, user_input: str, user_id: str, tenant_id: str, user_type: str) -> Dict:
        """
        VOLLSTÄNDIGER CHAT PROZESS
        1. Get/Create Session
        2. Detect Intent
        3. Generate Response
        4. Decide Routing
        5. Save Context
        """
        
        # 1. Session
        session = self.get_or_create_session(user_id, tenant_id)
        session.add_message('user', user_input)
        
        # 2. Intent Detection
        context = session.get_context()
        intent_result = self.intent_detector.detect(user_input, context)
        session.detected_intent = intent_result
        
        # 3. Response Generation
        response = self.response_generator.generate(
            user_input,
            intent_result,
            user_type,
            context
        )
        
        # 4. Add to session
        session.add_message('assistant', response['content'], {
            'intent': intent_result,
            'action': response['action']
        })
        
        return {
            'response': response['content'],
            'intent': intent_result['intents'],
            'action': response['action'],
            'route_to': response['route_to_brain'],
            'session_id': session.user_id
        }

