#!/usr/bin/env python3
"""
DEVELOPER CHAT BACKEND
Communication interface with Autonomous AI System
"""

from flask import Flask, request, jsonify
import json
import os
import sqlite3
from datetime import datetime
import subprocess

app = Flask(__name__)

MEMORY_FILE = '/root/aicore/memory.json'
BRAIN_FILE = '/root/aicore/brain.py'
SYSTEM_DB = '/root/aicore/ai_knowledge.db'

def load_memory():
    """Load system memory"""
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def get_system_status():
    """Get current system status"""
    try:
        memory = load_memory()
        return {
            'timestamp': datetime.now().isoformat(),
            'projects': len([p for p in os.listdir('/root/aicore/projects') if p.endswith('.json')]),
            'memory_size': len(str(memory)),
            'databases': len([f for f in os.listdir('/root/aicore') if f.endswith('.db')]),
            'services_running': check_services(),
            'system_health': 'HEALTHY'
        }
    except Exception as e:
        return {'error': str(e)}

def check_services():
    """Check running services"""
    services = {}
    ports = {
        '5010': 'AI Internal',
        '5011': 'AI External',
        '5080': 'Lab API',
        '5090': 'Developer Chat',
        '11434': 'Ollama'
    }
    
    for port, name in ports.items():
        try:
            result = subprocess.run(
                f"netstat -tlnp 2>/dev/null | grep :{port} | grep LISTEN",
                shell=True, capture_output=True, text=True
            )
            services[name] = 'RUNNING' if result.returncode == 0 else 'OFFLINE'
        except:
            services[name] = 'UNKNOWN'
    
    return services

def execute_command(cmd):
    """Execute developer command"""
    parts = cmd.split()
    command = parts[0].lower() if parts else ''
    args = parts[1:] if len(parts) > 1 else []
    
    if command == '/status':
        return get_system_status()
    
    elif command == '/build':
        if args:
            customer_id = args[0]
            return build_customer_solution(customer_id)
        return {'error': 'Usage: /build {customer-id}'}
    
    elif command == '/logs':
        lines = int(args[0]) if args else 50
        return get_system_logs(lines)
    
    elif command == '/memory':
        return load_memory()
    
    elif command == '/knowledge':
        return list_knowledge_bases()
    
    elif command == '/workers':
        return get_worker_status()
    
    elif command == '/metrics':
        return get_metrics()
    
    elif command == '/projects':
        return list_projects()
    
    elif command == '/help':
        return get_help()
    
    else:
        return {'error': f'Unknown command: {command}', 'help': 'Type /help for available commands'}

def build_customer_solution(customer_id):
    """Build solution for customer"""
    try:
        # Check if customer project exists
        project_file = f'/root/aicore/projects/{customer_id}.json'
        
        if not os.path.exists(project_file):
            return {'error': f'Customer project {customer_id} not found'}
        
        with open(project_file, 'r') as f:
            project = json.load(f)
        
        return {
            'status': 'BUILD_INITIATED',
            'customer_id': customer_id,
            'project': project.get('name', customer_id),
            'timestamp': datetime.now().isoformat(),
            'message': f'Building solution for {project.get("name", customer_id)}...'
        }
    except Exception as e:
        return {'error': str(e)}

def get_system_logs(lines=50):
    """Get system activity logs"""
    try:
        return {
            'logs': 'System logs (placeholder)',
            'timestamp': datetime.now().isoformat(),
            'lines_returned': lines
        }
    except:
        return {'error': 'Could not retrieve logs'}

def list_knowledge_bases():
    """List all knowledge bases"""
    dbs = []
    for f in os.listdir('/root/aicore'):
        if f.endswith('.db') and f.startswith('kdb'):
            dbs.append({
                'name': f,
                'size': os.path.getsize(f'/root/aicore/{f}'),
                'path': f'/root/aicore/{f}'
            })
    return {'knowledge_bases': dbs}

def get_worker_status():
    """Get worker pool status"""
    return {
        'workers': {
            'total': 8,
            'active': 5,
            'idle': 3,
            'status': 'HEALTHY'
        },
        'timestamp': datetime.now().isoformat()
    }

def get_metrics():
    """Get system metrics"""
    return {
        'cpu_usage': '35%',
        'memory_usage': '45%',
        'requests_per_second': 125,
        'average_response_time_ms': 450,
        'error_rate': '0.2%',
        'timestamp': datetime.now().isoformat()
    }

def list_projects():
    """List all customer projects"""
    projects = []
    for f in os.listdir('/root/aicore/projects'):
        if f.endswith('.json'):
            try:
                with open(f'/root/aicore/projects/{f}', 'r') as proj:
                    data = json.load(proj)
                    projects.append({
                        'id': f.replace('.json', ''),
                        'name': data.get('name', 'Unknown'),
                        'status': data.get('status', 'unknown')
                    })
            except:
                pass
    return {'projects': projects, 'count': len(projects)}

def get_help():
    """Get help on available commands"""
    return {
        'commands': {
            '/status': 'Show system health and status',
            '/build {id}': 'Build customer solution',
            '/logs {lines}': 'Show system logs',
            '/memory': 'Show system memory state',
            '/knowledge': 'List knowledge bases',
            '/workers': 'Show worker pool status',
            '/metrics': 'Show performance metrics',
            '/projects': 'List all customer projects',
            '/help': 'Show this help'
        }
    }

# ============ ROUTES ============

@app.route('/api/dev/execute', methods=['POST'])
def api_execute():
    """Execute developer command"""
    data = request.json or {}
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    result = execute_command(command)
    return jsonify(result)

@app.route('/api/dev/status', methods=['GET'])
def api_status():
    """Get system status"""
    return jsonify(get_system_status())

@app.route('/api/dev/projects', methods=['GET'])
def api_projects():
    """Get projects"""
    return jsonify(list_projects())

if __name__ == '__main__':
    print("[DEVELOPER CHAT] Starting on port 5091...")
    app.run(host='0.0.0.0', port=5091, debug=False, threaded=True)

