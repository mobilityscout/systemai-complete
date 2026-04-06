#!/usr/bin/env python3
"""
SYSTEM AI CHAT INTERFACE
Chat mit AI Developer - gibt Aufgaben, bekommt Optionen, entscheidet
"""

from flask import Flask, request, jsonify
import sys
sys.path.insert(0, '/root/aicore')

from ai_developer_brain import AIDevBrain

app = Flask(__name__)
dev_brain = AIDevBrain()

@app.route('/api/system/task', methods=['POST'])
def create_task():
    """System AI gibt Aufgabe zum AI Developer"""
    
    data = request.json or {}
    description = data.get('description', '')
    priority = data.get('priority', 'normal')
    
    task = dev_brain.receive_task(description, priority)
    
    # Analysiere sofort
    analysis = dev_brain.analyze_and_present_options(task.task_id)
    
    return jsonify({
        'task_id': task.task_id,
        'status': 'ready_for_decision',
        'analysis': analysis['analysis'],
        'options': analysis['options'],
        'message': 'Welche Option möchtest du?'
    })

@app.route('/api/system/task/<task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """System AI wählt Option und AI Developer führt aus"""
    
    data = request.json or {}
    option_number = data.get('option', 1)
    
    result = dev_brain.execute_selected_option(task_id, option_number)
    
    return jsonify(result)

@app.route('/api/system/status', methods=['GET'])
def status():
    """Status des AI Developer"""
    
    return jsonify(dev_brain.status())

if __name__ == '__main__':
    print("[SYSTEM AI CHAT] Starting...")
    print("💬 Chat mit AI Developer ist ready")
    print("")
    print("Endpoints:")
    print("  POST /api/system/task - Neue Aufgabe")
    print("  POST /api/system/task/<id>/execute - Führe Option aus")
    print("  GET /api/system/status - Status")
    
    app.run(host='127.0.0.1', port=5012, debug=False)

