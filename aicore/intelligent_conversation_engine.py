#!/usr/bin/env python3
"""
INTELLIGENT CONVERSATION ENGINE
Natürliche, tiefe Gespräche die User nicht durchschauen
Ermittelt Anforderungen implizit
Erstellt Projekte automatisch im Hintergrund
"""

import json
import os
from datetime import datetime
import uuid
import re

class ConversationAnalyzer:
    """
    SCHICHT 1: Tiefe Analyse (unsichtbar)
    Versteht echte Bedürfnisse hinter den Worten
    """
    
    def __init__(self):
        self.context = {}
        self.implicit_needs = []
    
    def deep_analyze(self, text, conversation_history):
        """
        TIEFE ANALYSE - User merkt NICHTS
        Nicht: "Ich merke confusion"
        Sondern: Aktiv Missverständnis auflösen
        """
        
        analysis = {
            'raw_text': text,
            'surface_level': self.analyze_surface(text),
            'deep_level': self.analyze_deep(text, conversation_history),
            'implicit_needs': self.extract_implicit_needs(text),
            'project_hints': self.find_project_hints(text),
            'relationship_state': self.assess_relationship(conversation_history)
        }
        
        return analysis
    
    def analyze_surface(self, text):
        """Was sagt der User oberflächlich?"""
        return {
            'length': len(text),
            'is_question': '?' in text,
            'is_greeting': any(g in text.lower() for g in ['hallo', 'hi', 'hey', 'wie geht']),
            'is_problem': any(p in text.lower() for p in ['problem', 'fehler', 'nicht', 'kaputt'])
        }
    
    def analyze_deep(self, text, history):
        """
        WAS BEDEUTET ES WIRKLICH?
        "Wie geht es dir?" = User baut Vertrauen auf
        = Beziehung wichtig vor Business
        = Anfangen mit Small Talk & Empathie
        """
        
        deep = {
            'user_intent_deep': [],
            'emotional_subtext': '',
            'relationship_building': False,
            'trust_level': self.assess_trust(history),
            'next_topic_hint': ''
        }
        
        text_lower = text.lower()
        
        # Beziehungsaufbau erkennen
        if any(g in text_lower for g in ['wie geht', 'danke', 'sorry', 'schön dich']):
            deep['relationship_building'] = True
            deep['emotional_subtext'] = 'User möchte Beziehung aufbauen vor Business'
            deep['user_intent_deep'].append('relationship')
        
        # Versteckte Probleme
        if 'nicht' in text_lower or 'aber' in text_lower:
            deep['user_intent_deep'].append('hidden_problem')
            deep['emotional_subtext'] = 'Etwas funktioniert nicht optimal'
        
        # Ideen/Visionen
        if any(w in text_lower for w in ['möchte', 'will', 'träume', 'stellt euch vor', 'würde gerne']):
            deep['user_intent_deep'].append('vision')
            deep['emotional_subtext'] = 'User hat Ideen/Wünsche'
        
        # Lernbereitschaft
        if any(w in text_lower for w in ['wie', 'zeig mir', 'lern', 'versteh']):
            deep['user_intent_deep'].append('learning')
            deep['emotional_subtext'] = 'User möchte verstehen & lernen'
        
        return deep
    
    def extract_implicit_needs(self, text):
        """
        VERSTECKTE BEDÜRFNISSE erkennen
        Nicht fragen "Was brauchst du?"
        Sondern: Aus Kontext ERKENNEN
        """
        
        needs = {
            'technical': [],
            'business': [],
            'creative': [],
            'support': []
        }
        
        text_lower = text.lower()
        
        # Technische Bedürfnisse
        tech_keywords = {
            'automation': ['automatisieren', 'schneller', 'optimieren'],
            'integration': ['verbinden', 'anbindung', 'schnittstelle'],
            'scaling': ['wächst', 'mehr', 'größer'],
            'security': ['sicher', 'schutz', 'privat']
        }
        
        for tech, keywords in tech_keywords.items():
            if any(kw in text_lower for kw in keywords):
                needs['technical'].append(tech)
        
        # Business Bedürfnisse
        business_keywords = {
            'efficiency': ['zeit', 'schneller', 'effizienz'],
            'revenue': ['umsatz', 'gewinn', 'mehr kunden'],
            'brand': ['marke', 'image', 'reputation'],
            'team': ['team', 'mitarbeiter', 'zusammenarbeit']
        }
        
        for biz, keywords in business_keywords.items():
            if any(kw in text_lower for kw in keywords):
                needs['business'].append(biz)
        
        # Kreative Bedürfnisse
        creative_keywords = {
            'design': ['design', 'schön', 'ästhetik'],
            'innovation': ['neu', 'anders', 'idea'],
            'storytelling': ['story', 'narrative', 'erzähl']
        }
        
        for crt, keywords in creative_keywords.items():
            if any(kw in text_lower for kw in keywords):
                needs['creative'].append(crt)
        
        return needs
    
    def find_project_hints(self, text):
        """
        PROJEKT HINTS finden
        "Ich könnte eine App bauen" = Projekt-Hint
        "Mein Team braucht bessere Tools" = Projekt-Hint
        """
        
        hints = {
            'scale': 0,
            'scope': None,
            'stakeholders': [],
            'timeline': None,
            'budget_range': None
        }
        
        text_lower = text.lower()
        
        # Größe/Scale
        if any(w in text_lower for w in ['klein', 'einfach']):
            hints['scale'] = 'small'
        elif any(w in text_lower for w in ['groß', 'komplex', 'enterprise']):
            hints['scale'] = 'large'
        else:
            hints['scale'] = 'medium'
        
        # Beteiligte
        if 'ich' in text_lower:
            hints['stakeholders'].append('owner')
        if any(w in text_lower for w in ['team', 'kollegen', 'mitarbeiter']):
            hints['stakeholders'].append('team')
        if any(w in text_lower for w in ['kunde', 'kunden', 'client']):
            hints['stakeholders'].append('customers')
        
        # Zeitrahmen
        if any(w in text_lower for w in ['sofort', 'dringend', 'jetzt']):
            hints['timeline'] = 'urgent'
        elif any(w in text_lower for w in ['nächste woche', 'nächsten monat']):
            hints['timeline'] = 'short_term'
        else:
            hints['timeline'] = 'flexible'
        
        return hints
    
    def assess_trust(self, history):
        """Wie vertraut User uns bereits?"""
        if not history:
            return 'new'
        if len(history) < 3:
            return 'building'
        if len(history) < 10:
            return 'established'
        return 'high'
    
    def assess_relationship(self, history):
        """Wie ist die Beziehung?"""
        if not history:
            return 'first_contact'
        
        # Analysiere letzten Austausch
        if len(history) > 0:
            last = history[-1]
            if 'dank' in last.get('input', '').lower():
                return 'appreciation'
            if '?' in last.get('input', ''):
                return 'inquiry'
        
        return 'neutral'


class ProjectDetector:
    """
    SCHICHT 2: Automatische Projekt-Erkennung
    Erstellt Projekte aus Gespräch (user merkt NICHTS)
    """
    
    def __init__(self, principle_id):
        self.principle_id = principle_id
        self.projects_dir = f'/root/aicore/principle_sots/{principle_id}/projects'
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def should_create_project(self, analysis):
        """Sollten wir ein Projekt erstellen?"""
        
        # Wenn User Probleme/Ideen hat
        if analysis['implicit_needs']['business'] or analysis['implicit_needs']['technical']:
            return True
        
        # Wenn Project Hints
        if analysis['project_hints']['stakeholders']:
            return True
        
        return False
    
    def generate_project(self, analysis, conversation_context):
        """
        Erstelle Projekt automatisch
        User kriegt davon nichts mit - passiert im Hintergrund
        """
        
        project_id = str(uuid.uuid4())[:8]
        
        project = {
            'id': project_id,
            'created': datetime.now().isoformat(),
            'status': 'auto_detected',
            'source': 'conversation',
            'name': self.generate_project_name(analysis),
            'description': self.generate_description(analysis),
            
            'requirements': {
                'technical': analysis['implicit_needs']['technical'],
                'business': analysis['implicit_needs']['business'],
                'creative': analysis['implicit_needs']['creative']
            },
            
            'scope': {
                'scale': analysis['project_hints']['scale'],
                'stakeholders': analysis['project_hints']['stakeholders'],
                'timeline': analysis['project_hints']['timeline']
            },
            
            'extracted_from': conversation_context,
            'confidence': self.calculate_confidence(analysis)
        }
        
        return project
    
    def generate_project_name(self, analysis):
        """Generiere intelligente Project Namen"""
        
        needs = analysis['implicit_needs']
        
        if needs['business']:
            primary = needs['business'][0].title()
            return f"{primary} Initiative"
        
        if needs['technical']:
            primary = needs['technical'][0].title()
            return f"{primary} System"
        
        return "Auto-Detected Project"
    
    def generate_description(self, analysis):
        """Generiere natürliche Beschreibung"""
        
        desc_parts = []
        
        if analysis['implicit_needs']['business']:
            desc_parts.append(
                f"Business Focus: {', '.join(analysis['implicit_needs']['business'])}"
            )
        
        if analysis['implicit_needs']['technical']:
            desc_parts.append(
                f"Technical Needs: {', '.join(analysis['implicit_needs']['technical'])}"
            )
        
        if analysis['project_hints']['stakeholders']:
            desc_parts.append(
                f"Involves: {', '.join(analysis['project_hints']['stakeholders'])}"
            )
        
        return " | ".join(desc_parts) if desc_parts else "Auto-detected project from conversation"
    
    def calculate_confidence(self, analysis):
        """Wie sicher sind wir dass das ein Projekt ist?"""
        
        confidence = 0.5  # Basis
        
        if analysis['implicit_needs']['business']:
            confidence += 0.2
        
        if analysis['implicit_needs']['technical']:
            confidence += 0.2
        
        if analysis['project_hints']['stakeholders']:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def save_project(self, project):
        """Speichere Projekt"""
        filename = f"{self.projects_dir}/{project['id']}.json"
        with open(filename, 'w') as f:
            json.dump(project, f, indent=2)
        
        return project


class NaturalResponseGenerator:
    """
    SCHICHT 3: Natürliche Responses
    User merkt NICHT dass dahinter Analyse/Projekte laufen
    """
    
    def generate(self, analysis, conversation_history, detected_project=None):
        """
        Generiere NATÜRLICHE Response
        - Keine "Ich merke"-Nachrichten
        - Echte menschliche Konversation
        - Aktiv zuhören & helfen
        """
        
        # Bestimme Response Type basierend auf tiefem Verständnis
        if analysis['deep_level']['relationship_building']:
            return self.respond_to_relationship_building(analysis)
        
        if analysis['deep_level']['user_intent_deep']:
            if 'hidden_problem' in analysis['deep_level']['user_intent_deep']:
                return self.respond_to_problem(analysis)
            
            if 'vision' in analysis['deep_level']['user_intent_deep']:
                return self.respond_to_vision(analysis, detected_project)
            
            if 'learning' in analysis['deep_level']['user_intent_deep']:
                return self.respond_to_learning_request(analysis)
        
        # Default: aktiv zuhören
        return self.respond_with_curiosity(analysis)
    
    def respond_to_relationship_building(self, analysis):
        """Antworte menschlich auf Beziehungsaufbau"""
        
        responses = [
            "Mir geht's gut, danke der Nachfrage! 😊 Wie kann ich dir heute helfen?",
            "Sehr gut, danke! Schön dich zu treffen. Was beschäftigt dich gerade?",
            "Alles klar! Ich freue mich auf unser Gespräch. Erzähl mir von dir.",
        ]
        
        return {
            'response': responses[0],
            'tone': 'warm',
            'visible_analysis': False
        }
    
    def respond_to_problem(self, analysis):
        """Antworte auf versteckte Probleme - aktiv zuhören"""
        
        return {
            'response': "Ich habe das Gefühl, dass da noch mehr dahintersteckt. Erzähl mir mehr - was genau funktioniert nicht so wie du es dir wünschst?",
            'tone': 'empathetic',
            'visible_analysis': False
        }
    
    def respond_to_vision(self, analysis, project=None):
        """Antworte auf Visionen & Ideen"""
        
        resp = "Das klingt spannend! 🚀 Lass mich verstehen - wenn das perfekt wäre, wie würde es aussehen?"
        
        if project:
            resp += " Und wen würde das alles betreffen?"
        
        return {
            'response': resp,
            'tone': 'excited',
            'visible_analysis': False
        }
    
    def respond_to_learning_request(self, analysis):
        """Antworte auf Lernwunsch"""
        
        return {
            'response': "Sehr gerne! Sag mir genau wo es unklar ist, dann erklär ich dir das Schritt für Schritt.",
            'tone': 'helpful',
            'visible_analysis': False
        }
    
    def respond_with_curiosity(self, analysis):
        """Standard: Mit echter Neugier antworten"""
        
        return {
            'response': "Interessant. Erzähl mir mehr - was ist dein eigentliches Ziel dabei?",
            'tone': 'curious',
            'visible_analysis': False
        }


class IntelligentConversationEngine:
    """
    HAUPTMOTOR - Alles zusammen
    User sieht NUR natürliche Konversation
    Im Hintergrund: Deep Analysis + Project Creation
    """
    
    def __init__(self, principle_id):
        self.principle_id = principle_id
        self.analyzer = ConversationAnalyzer()
        self.detector = ProjectDetector(principle_id)
        self.responder = NaturalResponseGenerator()
        self.conversation_history = []
    
    def process(self, user_input):
        """
        VOLLSTÄNDIGER PROZESS - User merkt NUR die Konversation
        """
        
        # 1. Tiefe Analyse (unsichtbar)
        analysis = self.analyzer.deep_analyze(user_input, self.conversation_history)
        
        # 2. Projekte erkennen & erstellen (unsichtbar)
        detected_project = None
        if self.detector.should_create_project(analysis):
            detected_project = self.detector.generate_project(analysis, user_input)
            self.detector.save_project(detected_project)
        
        # 3. NATÜRLICHE Response generieren (User sieht ONLY DAS)
        response = self.responder.generate(analysis, self.conversation_history, detected_project)
        
        # 4. Speichere History
        self.conversation_history.append({
            'input': user_input,
            'response': response['response'],
            'timestamp': datetime.now().isoformat(),
            'hidden_analysis': analysis,  # Im Backend gespeichert
            'project_created': detected_project is not None
        })
        
        # Return NUR die natürliche Response - keine Analyse sichtbar!
        return {
            'response': response['response'],
            'tone': response['tone'],
            'project_auto_created': detected_project is not None,
            'project_name': detected_project['name'] if detected_project else None,
            
            # Backend Info (nicht an User)
            '_internal': {
                'analysis': analysis,
                'project': detected_project
            }
        }

