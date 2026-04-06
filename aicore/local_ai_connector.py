#!/usr/bin/env python3
"""
LOCAL AI CONNECTOR
Integrates Ollama (local AI) into system loop
Makes your AI available as system service
"""

import requests
import json
import time
from datetime import datetime

class LocalAIConnector:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "mistral"  # or your preferred model
        self.status = "initializing"
        
    def health_check(self):
        """Check if Ollama is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                self.status = "online"
                return True
        except:
            self.status = "offline"
            return False
        return False
    
    def ask_ai(self, prompt, context=None):
        """Ask local AI (your own AI!)"""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"{context}\n\nQuestion: {prompt}"
            
            response = requests.post(
                self.ollama_url,
                json={
                    'model': self.model,
                    'prompt': full_prompt,
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            return None
        except Exception as e:
            print(f"[AI ERROR] {e}")
            return None
    
    def analyze_project(self, project_name, metrics):
        """Your AI analyzes a project"""
        prompt = f"""
        Project: {project_name}
        Metrics: {json.dumps(metrics, indent=2)}
        
        Analyze this project. Provide:
        1. Current status
        2. Issues detected
        3. Recommendations
        4. Next steps
        """
        return self.ask_ai(prompt)
    
    def generate_code(self, requirement):
        """Your AI generates code"""
        prompt = f"""
        Requirement: {requirement}
        
        Generate clean, production-ready Python code.
        Include comments and error handling.
        """
        return self.ask_ai(prompt)

# Global instance
ai_connector = None

def get_ai():
    """Get or initialize AI connector"""
    global ai_connector
    if ai_connector is None:
        ai_connector = LocalAIConnector()
    return ai_connector

if __name__ == "__main__":
    connector = LocalAIConnector()
    
    print("[AI] Checking Ollama availability...")
    if connector.health_check():
        print("[AI] ✅ Ollama is online!")
        
        # Test
        result = connector.ask_ai("What are you?")
        print(f"\n[AI RESPONSE]:\n{result}\n")
    else:
        print("[AI] ❌ Ollama not available")
        print("[AI] Start Ollama with: ollama serve")

