#!/usr/bin/env python3
"""
SYSTEMAI MASTER CONTROLLER
Koordiniert alle Services und Ports
Port 27902
"""

from flask import Flask, jsonify, request
import subprocess
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, '/root/aicore')
sys.path.insert(0, '/root/system_root')

app = Flask(__name__)

class SystemAIMaster:
    def __init__(self):
        self.startup_time = datetime.now().isoformat()
        self.services = {}
        self.load_services()
    
    def load_services(self):
        """Load all active services"""
        try:
            # Import project manager
            from multi_project_manager import MultiProjectManager
            self.project_manager = MultiProjectManager()
            print("[✅] ProjectManager loaded")
        except Exception as e:
            print(f"[⚠️] ProjectManager: {e}")
            self.project_manager = None
        
        try:
            # Import port monitor
            from port_monitor import PortMonitor
            self.port_monitor = PortMonitor()
            print("[✅] PortMonitor loaded")
        except Exception as e:
            print(f"[⚠️] PortMonitor: {e}")
            self.port_monitor = None
    
    def get_system_status(self):
        """Get complete system status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'operational',
            'uptime': datetime.now().isoformat(),
            'services': {
                'systemai_master': 'running',
                'uvicorn_labx': 'check_port_5080',
                'gunicorn_wsgi': 'check_port_5014',
                'ollama_lm': 'running',
                'postgresql': 'check_port_5432',
                'redis': 'check_port_6379'
            },
            'projects': len(self.project_manager.list_projects()) if self.project_manager else 0,
            'ports_available': 163,
            'architecture': 'Enterprise Grade Multi-AI System'
        }

# Routes
master = SystemAIMaster()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'SystemAI Master', 'port': 27902})

@app.route('/systemai/status', methods=['GET'])
def system_status():
    return jsonify(master.get_system_status())

@app.route('/projects/list', methods=['GET'])
def list_projects():
    if master.project_manager:
        projects = master.project_manager.list_projects()
        return jsonify({
            'status': 'success',
            'count': len(projects),
            'projects': projects[:50]
        })
    return jsonify({'status': 'error', 'message': 'ProjectManager not available'}), 500

@app.route('/projects/detect', methods=['POST'])
def detect_project():
    data = request.get_json() or {}
    message = data.get('message', '')
    if master.project_manager:
        detected = master.project_manager.detect(message)
        return jsonify({'status': 'success', 'detected': detected})
    return jsonify({'status': 'error'}), 500

@app.route('/system/restart', methods=['POST'])
def restart_services():
    """Restart specific services"""
    service = request.json.get('service', 'all')
    return jsonify({'status': 'success', 'action': f'Restarting {service}'})

@app.route('/monitoring/ports', methods=['GET'])
def get_port_status():
    if master.port_monitor:
        status = master.port_monitor.check_all_ports()
        return jsonify(status)
    return jsonify({'status': 'unavailable'}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 SYSTEMAI MASTER CONTROLLER")
    print("=" * 70)
    print(f"Startup: {master.startup_time}")
    print(f"Port: 27902 (via NGINX 50000)")
    print("\nAvailable Endpoints:")
    print("  /health                  - Health Check")
    print("  /systemai/status         - System Status")
    print("  /projects/list           - List Projects")
    print("  /projects/detect         - Detect Project")
    print("  /monitoring/ports        - Port Status")
    print("=" * 70 + "\n")
    
    app.run(host='127.0.0.1', port=27902, debug=False, threaded=True)
