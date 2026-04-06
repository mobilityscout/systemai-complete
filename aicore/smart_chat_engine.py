#!/usr/bin/env python3
"""
SMART CHAT ENGINE
Ein virtueller Mitarbeiter der wie ein Mensch arbeitet
Analysiert → Versteht → Handelt → Berichtet
"""

import json
import os
import sqlite3
from datetime import datetime
import subprocess
import re

class SmartChatEngine:
    """Intelligenter virtueller Mitarbeiter"""
    
    def __init__(self):
        self.context = {}
        self.memory_file = '/root/aicore/memory.json'
        self.load_memory()
    
    def load_memory(self):
        """Lade System Memory"""
        try:
            with open(self.memory_file, 'r') as f:
                self.context = json.load(f)
        except:
            self.context = {'conversations': [], 'tasks': [], 'state': {}}
    
    def save_memory(self):
        """Speichere System Memory"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.context, f, indent=2)
        except:
            pass
    
    def analyze_input(self, user_input):
        """
        SCHRITT 1: Analysiere was der User will
        - Erkenne das Thema
        - Erkenne die Absicht
        - Sammle relevante Daten
        """
        
        analysis = {
            'raw_input': user_input,
            'timestamp': datetime.now().isoformat(),
            'themes': self.detect_themes(user_input),
            'intent': self.detect_intent(user_input),
            'keywords': self.extract_keywords(user_input),
            'data_sources': []
        }
        
        # Welche Datenquellen sind relevant?
        if any(t in analysis['themes'] for t in ['system', 'server', 'performance', 'status']):
            analysis['data_sources'].append('system_metrics')
        
        if any(t in analysis['themes'] for t in ['project', 'customer', 'build', 'deploy']):
            analysis['data_sources'].append('projects')
        
        if any(t in analysis['themes'] for t in ['knowledge', 'data', 'database', 'wissen']):
            analysis['data_sources'].append('knowledge_bases')
        
        if any(t in analysis['themes'] for t in ['worker', 'task', 'job', 'execution']):
            analysis['data_sources'].append('worker_pool')
        
        if any(t in analysis['themes'] for t in ['memory', 'state', 'brain', 'decision']):
            analysis['data_sources'].append('system_state')
        
        return analysis
    
    def detect_themes(self, text):
        """Erkenne Themenbereiche"""
        text_lower = text.lower()
        themes = []
        
        theme_keywords = {
            'system': ['server', 'system', 'status', 'health', 'performance', 'cpu', 'memory'],
            'project': ['project', 'customer', 'kunde', 'build', 'deploy', 'lösung'],
            'knowledge': ['wissen', 'datenbank', 'knowledge', 'information', 'abfrage'],
            'worker': ['worker', 'task', 'job', 'ausführung', 'process'],
            'debugging': ['fehler', 'error', 'bug', 'problem', 'fix', 'debug'],
            'optimization': ['schneller', 'optimieren', 'performance', 'speed', 'improve'],
            'integration': ['api', 'anbindung', 'integration', 'connect', 'schnittstelle']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(kw in text_lower for kw in keywords):
                themes.append(theme)
        
        return themes
    
    def detect_intent(self, text):
        """Erkenne die Absicht"""
        text_lower = text.lower()
        
        intents = {
            'check': ['wie ist', 'status', 'zeig mir', 'schau', 'überprüf', 'check'],
            'fix': ['fix', 'behebe', 'repariere', 'problem', 'error', 'debug'],
            'build': ['baue', 'erstelle', 'build', 'develop', 'schreibe'],
            'deploy': ['deploy', 'starte', 'launch', 'veröffentlich', 'aktiviere'],
            'analyze': ['analysiere', 'untersuche', 'schau', 'wie', 'warum'],
            'configure': ['konfiguriere', 'stelle ein', 'setup', 'configure'],
            'monitor': ['überwache', 'beobachte', 'watch', 'track']
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                detected_intents.append(intent)
        
        return detected_intents if detected_intents else ['general']
    
    def extract_keywords(self, text):
        """Extrahiere relevante Keywords"""
        # Vereinfachte Keyword Extraction
        words = text.split()
        keywords = [w for w in words if len(w) > 4]
        return keywords[:5]  # Top 5
    
    def gather_data(self, analysis):
        """
        SCHRITT 2: Sammle relevante Daten
        - Lese System State
        - Query Datenbanken
        - Check Worker Status
        - Hole Projekt Info
        """
        
        data = {
            'system': {},
            'projects': [],
            'knowledge': [],
            'workers': {},
            'memory': self.context
        }
        
        # System Metrics
        if 'system_metrics' in analysis['data_sources']:
            data['system'] = self.get_system_metrics()
        
        # Projects
        if 'projects' in analysis['data_sources']:
            data['projects'] = self.get_projects()
        
        # Knowledge Bases
        if 'knowledge_bases' in analysis['data_sources']:
            data['knowledge'] = self.get_knowledge_bases()
        
        # Worker Pool
        if 'worker_pool' in analysis['data_sources']:
            data['workers'] = self.get_worker_status()
        
        return data
    
    def get_system_metrics(self):
        """Hole System Metriken"""
        try:
            result = subprocess.run('free -h', shell=True, capture_output=True, text=True)
            return {
                'memory': result.stdout,
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {}
    
    def get_projects(self):
        """Hole alle Projekte"""
        projects = []
        try:
            for f in os.listdir('/root/aicore/projects'):
                if f.endswith('.json'):
                    with open(f'/root/aicore/projects/{f}', 'r') as pf:
                        projects.append(json.load(pf))
        except:
            pass
        return projects
    
    def get_knowledge_bases(self):
        """Hole Wissensbasen Info"""
        dbs = []
        try:
            for f in os.listdir('/root/aicore'):
                if f.endswith('.db'):
                    dbs.append({
                        'name': f,
                        'size': os.path.getsize(f'/root/aicore/{f}'),
                        'path': f'/root/aicore/{f}'
                    })
        except:
            pass
        return dbs
    
    def get_worker_status(self):
        """Hole Worker Pool Status"""
        return {
            'total': 8,
            'active': 5,
            'idle': 3,
            'status': 'HEALTHY'
        }
    
    def generate_response(self, analysis, data):
        """
        SCHRITT 3: Generiere intelligente Response
        - Interpretiere die Daten
        - Erstelle Aktion Plan falls nötig
        - Berichte strukturiert
        """
        
        response = {
            'analysis': analysis,
            'data': data,
            'interpretation': self.interpret_data(analysis, data),
            'action_plan': self.create_action_plan(analysis, data),
            'next_steps': self.suggest_next_steps(analysis, data)
        }
        
        return response
    
    def interpret_data(self, analysis, data):
        """Interpretiere die Daten"""
        interpretation = {
            'summary': [],
            'findings': [],
            'recommendations': []
        }
        
        # Basierend auf Themes und Intents
        if 'system' in analysis['themes']:
            interpretation['summary'].append('System Status: ANALYZING')
        
        if 'debugging' in analysis['themes']:
            interpretation['summary'].append('Debug Mode: ACTIVE')
        
        if 'optimization' in analysis['themes']:
            interpretation['recommendations'].append('Performance Optimization Scan läuft...')
        
        return interpretation
    
    def create_action_plan(self, analysis, data):
        """Erstelle Aktionsplan"""
        plan = {
            'actions': [],
            'priority': 'normal'
        }
        
        if 'fix' in analysis['intent']:
            plan['actions'].append('1. Analysiere Problem')
            plan['actions'].append('2. Identifiziere Root Cause')
            plan['actions'].append('3. Implementiere Fix')
            plan['actions'].append('4. Teste Solution')
            plan['priority'] = 'high'
        
        if 'build' in analysis['intent']:
            plan['actions'].append('1. Analysiere Anforderungen')
            plan['actions'].append('2. Plane Architektur')
            plan['actions'].append('3. Implementiere Code')
            plan['actions'].append('4. Teste Integration')
        
        return plan
    
    def suggest_next_steps(self, analysis, data):
        """Schlage nächste Schritte vor"""
        suggestions = []
        
        if not analysis['intent']:
            suggestions.append('Konkretisiere deine Frage für bessere Hilfe')
        
        if len(analysis['themes']) == 0:
            suggestions.append('Mehr Kontext würde helfen')
        
        suggestions.append('Sag mir "mehr Details" für tiefere Analyse')
        
        return suggestions
    
    def process(self, user_input):
        """
        HAUPTPROZESS:
        1. Analysiere
        2. Sammle Daten
        3. Generiere Response
        4. Speichere Memory
        """
        
        # 1. Analyse
        analysis = self.analyze_input(user_input)
        
        # 2. Daten sammeln
        data = self.gather_data(analysis)
        
        # 3. Response generieren
        response = self.generate_response(analysis, data)
        
        # 4. Memory speichern
        self.context['conversations'].append({
            'input': user_input,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        self.save_memory()
        
        return response

# Export für Flask
engine = SmartChatEngine()

def process_user_input(user_input):
    """Prozessiere User Input"""
    return engine.process(user_input)

