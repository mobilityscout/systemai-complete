#!/usr/bin/env python3
"""
AI TRAINER - Learn from examples
Feed your AI with custom knowledge
"""

import sqlite3
from datetime import datetime
import json

DB_PATH = '/root/aicore/ai_knowledge.db'

def init_knowledge_db():
    """Initialize knowledge base"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY,
        category TEXT,
        question TEXT,
        answer TEXT,
        timestamp TEXT,
        usage_count INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def add_knowledge(category, question, answer):
    """Add learned knowledge"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO knowledge (category, question, answer, timestamp)
                 VALUES (?, ?, ?, ?)''',
              (category, question, answer, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"✅ Learned: {category} - {question[:50]}")

def get_knowledge(category=None):
    """Get knowledge base"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if category:
        c.execute('''SELECT question, answer FROM knowledge WHERE category = ?''', (category,))
    else:
        c.execute('''SELECT category, question, answer FROM knowledge''')
    results = c.fetchall()
    conn.close()
    return results

def train_from_file(file_path):
    """Load training data from JSON file"""
    with open(file_path) as f:
        data = json.load(f)
    
    for item in data:
        add_knowledge(
            item.get('category', 'general'),
            item.get('question', ''),
            item.get('answer', '')
        )

# Example usage
if __name__ == '__main__':
    init_knowledge_db()
    
    # Add some training examples
    training_data = [
        {
            'category': 'System',
            'question': 'What is this system?',
            'answer': 'This is Global AI Project System - a unified platform for multi-region project management with local Ollama AI'
        },
        {
            'category': 'System',
            'question': 'How do I create a project?',
            'answer': 'Go to /projects page, fill in project name, select region (EU/APAC/AMERICAS), click Create'
        },
        {
            'category': 'AI',
            'question': 'Can you speak German?',
            'answer': 'Ja, ich kann Deutsch sprechen! Du kannst mit mir auf Deutsch kommunizieren.'
        }
    ]
    
    for data in training_data:
        add_knowledge(data['category'], data['question'], data['answer'])
    
    print("\n✅ Knowledge base trained!")
    print("\nLearned knowledge:")
    for kb in get_knowledge():
        print(f"  • {kb}")

