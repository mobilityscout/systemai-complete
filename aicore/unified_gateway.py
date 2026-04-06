#!/usr/bin/env python3
"""
UNIFIED GATEWAY - Mit Chat Assistant
Routes through Master Brain + Chat Intelligence
"""

from flask import Flask, request, jsonify
import sys
import os
import uuid

sys.path.insert(0, '/root/aicore/core')
sys.path.insert(0, '/root/aicore/internal')
sys.path.insert(0, '/root/aicore/external')
sys.path.insert(0, '/root/aicore/shared')

from master_brain import MasterBrain
from chat_assistant import ChatAssistant
from cache_layer import CacheLayer
from auth_service import AuthService

app = Flask(__name__)

master_brain = MasterBrain()
chat_assistant = ChatAssistant()
cache = CacheLayer()
auth = AuthService("your-secret-key-here")

@app.route('/', methods=['GET'])
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>System AI - GitHub + Copilot Replacement</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                text-align: center;
                color: white;
                max-width: 900px;
            }
            h1 { font-size: 3em; margin-bottom: 20px; }
            p { font-size: 1.2em; margin-bottom: 40px; opacity: 0.9; }
            .grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-top: 40px;
            }
            .card {
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 12px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .card h3 { margin-bottom: 10px; font-size: 1.5em; }
            .card p { font-size: 0.95em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 System AI</h1>
            <p>GitHub + Copilot Replacement</p>
            
            <div class="grid">
                <div class="card">
                    <h3>💻 Code Generation</h3>
                    <p>Wie Copilot - schreib Code auf Deutsch</p>
                </div>
                <div class="card">
                    <h3>🔀 Pull Requests</h3>
                    <p>Auto-create PRs, Reviews, Merges</p>
                </div>
                <div class="card">
                    <h3>📋 Issue Tracker</h3>
                    <p>Automatisch aus Conversations</p>
                </div>
                <div class="card">
                    <h3>🚀 Deployment</h3>
                    <p>Auto-Deploy Pipelines</p>
                </div>
                <div class="card">
                    <h3>👥 Team Collab</h3>
                    <p>Code Reviews & Discussions</p>
                </div>
                <div class="card">
                    <h3>🔐 Security</h3>
                    <p>Internal/External Isolation</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Main Chat Endpoint"""
    
    data = request.json or {}
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_input = data.get('input', '').strip()
    
    if not user_input:
        return jsonify({'error': 'No input'}), 400
    
    # 1. Authenticate via Master Brain
    user_auth = master_brain.authenticate_user(token)
    if not user_auth.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = user_auth.get('user_id') or str(uuid.uuid4())
    tenant_id = user_auth.get('tenant_id') or 'default'
    user_type = user_auth.get('user_type').value if user_auth.get('user_type') else 'external'
    
    # 2. Process through Chat Assistant
    chat_result = chat_assistant.process(user_input, user_id, tenant_id, user_type)
    
    # 3. Route through Master Brain
    request_data = {
        'action': chat_result['action'],
        'input': user_input,
        'tenant_id': tenant_id,
        'intent': chat_result['intent']
    }
    
    routing = master_brain.route_request(user_auth, request_data)
    
    # 4. Execute
    if not routing['allowed'] and chat_result['route_to']:
        # Override routing if Master Brain says no
        if chat_result['route_to'] == 'internal' and user_type != 'internal':
            return jsonify({
                'response': '🔐 Das ist nur für interne Teams verfügbar.',
                'blocked': True
            })
    
    result = master_brain.execute_request(routing, request_data)
    
    return jsonify({
        'response': chat_result['response'],
        'intent': chat_result['intent'],
        'action': chat_result['action'],
        'routing': routing['target_brain'],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    from datetime import datetime
    print("[UNIFIED GATEWAY] Starting with Chat Assistant...")
    print("🔴 Master Brain (Orchestrator)")
    print("💬 Chat Assistant (Natural Language)")
    print("🟢 Internal Brain (Server Access)")
    print("🔵 External Brain (Product)")
    print("")
    print("Access: http://51.24.14.6:50000")
    print("")
    print("Ready for:")
    print("✓ Code Generation (Copilot)")
    print("✓ Pull Requests (GitHub)")
    print("✓ Issue Tracking (GitHub)")
    print("✓ Deployments (DevOps)")
    print("✓ Team Collaboration")
    app.run(host='0.0.0.0', port=50000, debug=False, threaded=True)

