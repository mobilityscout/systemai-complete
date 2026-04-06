#!/usr/bin/env python3
"""
PRINCIPLE BRAIN - System AI für den Owner
Das Gehirn von Principle
Liest aus Principle SOT, macht Entscheidungen, lernt
"""

import json
import os
from datetime import datetime
import hashlib

class PrincipleSOT:
    """Single Source of Truth für einen Principle"""
    
    def __init__(self, principle_id):
        self.principle_id = principle_id
        self.sot_file = f'/root/aicore/principle_sots/{principle_id}/sot.json'
        self.history_file = f'/root/aicore/principle_sots/{principle_id}/history.json'
        
        # Stelle sicher dass Directories existieren
        os.makedirs(os.path.dirname(self.sot_file), exist_ok=True)
        
        self.sot = self.load_sot()
        self.history = self.load_history()
    
    def load_sot(self):
        """Lade Principle SOT"""
        if os.path.exists(self.sot_file):
            with open(self.sot_file, 'r') as f:
                return json.load(f)
        
        # Template für neue Principle
        return {
            'principle_id': self.principle_id,
            'created': datetime.now().isoformat(),
            'values': {},  # Prinzipien/Werte
            'blueprints': {},  # Templates für Lösungen
            'decision_rules': {},  # Entscheidungsregeln
            'knowledge': {},  # Gesamtwissen
            'customers': {},  # Kunden im SOT
            'learnings': []  # Was das System gelernt hat
        }
    
    def load_history(self):
        """Lade Conversation History"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {'conversations': []}
    
    def save(self):
        """Speichere SOT"""
        with open(self.sot_file, 'w') as f:
            json.dump(self.sot, f, indent=2)
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_value(self, key, value, description=''):
        """Füge Prinzip/Wert hinzu"""
        self.sot['values'][key] = {
            'value': value,
            'description': description,
            'added': datetime.now().isoformat()
        }
        self.save()
    
    def add_blueprint(self, name, blueprint_data):
        """Füge Blueprint hinzu"""
        self.sot['blueprints'][name] = {
            'data': blueprint_data,
            'created': datetime.now().isoformat(),
            'uses': 0
        }
        self.save()
    
    def add_learning(self, learning):
        """Speichere Learnings"""
        self.sot['learnings'].append({
            'learning': learning,
            'timestamp': datetime.now().isoformat()
        })
        self.save()
    
    def add_conversation(self, user_input, response, context):
        """Speichere Conversation"""
        self.history['conversations'].append({
            'timestamp': datetime.now().isoformat(),
            'input': user_input,
            'response_summary': response[:100],
            'context': context
        })
        self.save()


class PrincipleBrain:
    """Das Gehirn von Principle - macht Entscheidungen für Owner"""
    
    def __init__(self, principle_id):
        self.principle_id = principle_id
        self.sot = PrincipleSOT(principle_id)
        self.conversation_count = 0
    
    def understand_user(self, user_input, is_principle=False):
        """
        VERSTEHE was User will
        - Nutze Principle SOT als Context
        - Erkenne ob Frage zum Principle gehört
        - Erkenne emotionalen State
        """
        
        analysis = {
            'user_input': user_input,
            'is_principle_question': is_principle,
            'emotion': self.detect_emotion(user_input),
            'danger_level': self.detect_danger(user_input),
            'intent': self.detect_intent(user_input),
            'relevant_blueprints': []
        }
        
        # Wenn es um Principle geht - nutze sein SOT
        if is_principle or any(word in user_input.lower() for word in ['principle', 'mein', 'meine', 'unser']):
            analysis['principle_relevant'] = True
            # Finde relevante Blueprints
            analysis['relevant_blueprints'] = self.find_relevant_blueprints(user_input)
        
        return analysis
    
    def detect_emotion(self, text):
        """Erkenne emotionalen State"""
        text_lower = text.lower()
        
        emotions = {
            'frustrated': ['frustrier', 'angry', 'problem', 'fehler', 'nicht', 'kann nicht'],
            'confused': ['versteh', 'wie', 'warum', 'nicht klar', 'confused'],
            'excited': ['toll', 'super', 'amazing', 'great', 'love', 'begeister'],
            'sad': ['traurig', 'sad', 'unglücklich', 'deprimier'],
            'anxious': ['angst', 'nervös', 'worried', 'stress', 'druck'],
            'neutral': []
        }
        
        detected = []
        for emotion, keywords in emotions.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(emotion)
        
        return detected if detected else ['neutral']
    
    def detect_danger(self, text):
        """Erkenne potenzielle Gefahren"""
        text_lower = text.lower()
        
        danger_keywords = {
            'security': ['hack', 'sicherheit', 'breach', 'password', 'attack', 'security'],
            'data_loss': ['löschen', 'delete', 'verlust', 'backup', 'verloren'],
            'financial': ['geld', 'kosten', 'schulden', 'bankrott', 'finanz'],
            'health': ['krank', 'verletzt', 'gesundheit', 'health', 'injury'],
            'legal': ['gesetz', 'recht', 'legal', 'court', 'anwalt']
        }
        
        dangers = []
        danger_level = 'low'
        
        for danger_type, keywords in danger_keywords.items():
            if any(kw in text_lower for kw in keywords):
                dangers.append(danger_type)
                danger_level = 'high'
        
        return {
            'dangers': dangers,
            'level': danger_level,
            'needs_alert': len(dangers) > 0
        }
    
    def detect_intent(self, text):
        """Erkenne Absicht des Users"""
        text_lower = text.lower()
        
        intents = {
            'learn': ['wie', 'zeig mir', 'erklär', 'teach', 'lern'],
            'build': ['baue', 'erstelle', 'mach', 'develop', 'build'],
            'fix': ['fix', 'behebe', 'repariere', 'problem', 'debug'],
            'analyze': ['analysiere', 'schau', 'check', 'untersuch', 'versteh'],
            'decide': ['sollte ich', 'was ist besser', 'welcher', 'entscheid'],
            'relationship': ['hallo', 'wie geht', 'danke', 'small talk']
        }
        
        detected = []
        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(intent)
        
        return detected if detected else ['general']
    
    def find_relevant_blueprints(self, query):
        """Finde relevante Blueprints für Query"""
        relevant = []
        query_lower = query.lower()
        
        for blueprint_name in self.sot.sot['blueprints']:
            if any(word in query_lower for word in blueprint_name.lower().split('_')):
                relevant.append(blueprint_name)
        
        return relevant
    
    def respond_with_principle(self, user_input, analysis):
        """
        ANTWORTE als Principle Brain
        - Nutze SOT Wissen
        - Beachte Emotions
        - Erkenne Danger
        - Nutze Blueprints
        - Lerne dazu
        """
        
        response = {
            'analysis': analysis,
            'response_type': 'principle_aware',
            'content': '',
            'actions': [],
            'learning': None,
            'danger_alert': None
        }
        
        # DANGER DETECTION
        if analysis['danger_level']['needs_alert']:
            response['danger_alert'] = {
                'level': analysis['danger_level']['level'],
                'dangers': analysis['danger_level']['dangers'],
                'message': f'⚠️ ACHTUNG: {", ".join(analysis["danger_level"]["dangers"])} erkannt!'
            }
        
        # EMOTION HANDLING
        emotions = analysis['emotion']
        if 'frustrated' in emotions:
            response['content'] = "Ich sehe dass du frustriert bist. Lass mich dir helfen..."
        elif 'excited' in emotions:
            response['content'] = "Das freut mich! Lass uns das zusammen umsetzen..."
        elif 'confused' in emotions:
            response['content'] = "Verstanden - das ist unklar. Lass mich erklären..."
        elif 'anxious' in emotions:
            response['content'] = "Keine Sorge, ich bin hier um dich zu unterstützen..."
        else:
            response['content'] = "Verstanden. Lass mich analysieren..."
        
        # BLUEPRINT USAGE
        if analysis['relevant_blueprints']:
            response['actions'].append({
                'action': 'use_blueprints',
                'blueprints': analysis['relevant_blueprints']
            })
        
        # LEARNINGS
        if any(word in user_input.lower() for word in ['neu', 'gelernt', 'idea', 'gedanke']):
            response['learning'] = {
                'type': 'new_insight',
                'content': user_input,
                'will_save_to_sot': True
            }
        
        return response
    
    def process(self, user_input, is_principle=False):
        """
        HAUPTPROZESS:
        1. Verstehe User & Context
        2. Erkenne Emotion & Danger
        3. Antworte mit Principle Brain
        4. Speichere Learning
        5. Update SOT
        """
        
        self.conversation_count += 1
        
        # 1. Verstehe
        analysis = self.understand_user(user_input, is_principle)
        
        # 2. Antworte mit Principle Brain
        response = self.respond_with_principle(user_input, analysis)
        
        # 3. Speichere Conversation
        self.sot.add_conversation(
            user_input,
            response['content'],
            {
                'emotion': analysis['emotion'],
                'danger': analysis['danger_level'],
                'intent': analysis['intent']
            }
        )
        
        # 4. Speichere Learning wenn vorhanden
        if response['learning']:
            self.sot.add_learning(response['learning']['content'])
        
        return response

# Export
def get_principle_brain(principle_id):
    """Get Brain für Principle"""
    return PrincipleBrain(principle_id)

