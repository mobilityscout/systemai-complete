#!/usr/bin/env python3
"""
SYSTEMAI ENTERPRISE CONTROL PLANE
Port 50000 (via NGINX)
Professional Monitoring & Management Dashboard
"""

from flask import Flask, render_template_string, jsonify, request
import requests
import json
import subprocess
from datetime import datetime
from collections import defaultdict
import psutil
import sys

sys.path.insert(0, '/root/aicore')
sys.path.insert(0, '/root/system_root')

app = Flask(__name__)

class EnterpriseControlPlane:
    def __init__(self):
        self.master_url = 'http://127.0.0.1:27902'
        self.dashboard_url = 'http://127.0.0.1:6400'
        self.startup_time = datetime.now().isoformat()
        self.metrics_history = defaultdict(list)
    
    def get_all_services_status(self):
        """Get status of all services"""
        services = {
            'master_controller': self._check_service(27902),
            'dashboard': self._check_service(6400),
            'uvicorn': self._check_service(5080),
            'gunicorn': self._check_service(5014),
            'postgresql': self._check_service(5432),
            'redis': self._check_service(6379),
            'ollama': self._check_service(11434),
        }
        
        # Add extension ports status
        for port_range, name in [
            ((6400, 6421), 'external_apis'),
            ((6500, 6503), 'message_queues'),
            ((6600, 6603), 'monitoring'),
            ((6700, 6702), 'development'),
            ((6703, 6832), 'reserved'),
        ]:
            services[name] = self._check_port_range(port_range[0], port_range[1])
        
        return services
    
    def _check_service(self, port):
        """Check if service is running"""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], 
                                  capture_output=True, timeout=2)
            return 'running' if result.returncode == 0 else 'down'
        except:
            return 'unknown'
    
    def _check_port_range(self, start, end):
        """Check active ports in range"""
        try:
            result = subprocess.run(['lsof', '-i', '-P', '-n'], 
                                  capture_output=True, text=True, timeout=5)
            count = 0
            for line in result.stdout.split('\n'):
                for port in range(start, end + 1):
                    if f':{port}' in line and 'LISTEN' in line:
                        count += 1
            return {'status': 'active', 'count': count, 'total': (end - start + 1)}
        except:
            return {'status': 'unknown', 'count': 0}
    
    def get_system_metrics(self):
        """Get system performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg(),
        }
    
    def get_projects_summary(self):
        """Get project summary from master"""
        try:
            r = requests.get(f'{self.master_url}/projects/list', timeout=2)
            data = r.json()
            return data
        except:
            return {'status': 'error', 'count': 0}
    
    def control_service(self, action, service):
        """Control services - start/stop/restart"""
        if action == 'restart':
            if service == 'master':
                subprocess.Popen(['pkill', '-f', 'systemai_master.py'])
                subprocess.Popen(['python3', '/root/aicore/systemai_master.py'])
                return {'status': 'restarting', 'service': 'master'}
        return {'status': 'ok'}

control_plane = EnterpriseControlPlane()

# ============ HTML ENTERPRISE DASHBOARD ============

ENTERPRISE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SystemAI Enterprise Control Plane</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }
        
        .navbar {
            background: rgba(0, 0, 0, 0.8);
            border-bottom: 2px solid #00ff88;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .navbar h1 {
            font-size: 24px;
            color: #00ff88;
            font-weight: 600;
        }
        
        .navbar-right {
            display: flex;
            gap: 30px;
            align-items: center;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-healthy { background: #00ff88; }
        .status-warning { background: #ffcc00; }
        .status-critical { background: #ff3333; }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px;
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            border-color: #00ff88;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }
        
        .card h3 {
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 6px;
        }
        
        .metric-label { font-size: 12px; color: #aaa; }
        .metric-value { font-size: 18px; color: #00ff88; font-weight: 600; }
        
        .service-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: rgba(0, 0, 0, 0.2);
            border-left: 3px solid #00ff88;
            margin: 8px 0;
            border-radius: 4px;
        }
        
        .service-name { font-weight: 500; }
        .service-status { font-size: 12px; }
        
        .btn {
            background: #00ff88;
            color: #0f0f23;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 12px;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #00dd77;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #444;
            color: #fff;
        }
        
        .btn-secondary:hover {
            background: #555;
        }
        
        .chart-container {
            position: relative;
            height: 250px;
            margin: 20px 0;
        }
        
        .alert {
            background: rgba(255, 51, 51, 0.1);
            border-left: 4px solid #ff3333;
            padding: 15px;
            margin: 15px 0;
            border-radius: 6px;
            color: #ff6666;
        }
        
        .alert.warning {
            background: rgba(255, 204, 0, 0.1);
            border-left-color: #ffcc00;
            color: #ffdd66;
        }
        
        .alert.success {
            background: rgba(0, 255, 136, 0.1);
            border-left-color: #00ff88;
            color: #66ff99;
        }
        
        .port-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }
        
        .port-badge {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.5);
            padding: 10px;
            border-radius: 6px;
            text-align: center;
            font-size: 12px;
        }
        
        .port-badge.active {
            background: rgba(0, 255, 136, 0.2);
            border-color: #00ff88;
        }
        
        footer {
            text-align: center;
            padding: 30px;
            color: #666;
            border-top: 1px solid rgba(0, 255, 136, 0.2);
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🚀 SystemAI Enterprise Control Plane</h1>
        <div class="navbar-right">
            <div>Last Updated: <span id="update-time">--:--:--</span></div>
            <button class="btn btn-secondary" onclick="location.reload()">Refresh</button>
        </div>
    </div>
    
    <div class="container">
        <!-- SYSTEM METRICS -->
        <div class="grid-4">
            <div class="card">
                <h3>CPU Usage</h3>
                <div class="metric">
                    <span class="metric-label">Utilization</span>
                    <span class="metric-value" id="cpu">--%</span>
                </div>
            </div>
            <div class="card">
                <h3>Memory Usage</h3>
                <div class="metric">
                    <span class="metric-label">Utilization</span>
                    <span class="metric-value" id="memory">--%</span>
                </div>
            </div>
            <div class="card">
                <h3>Disk Usage</h3>
                <div class="metric">
                    <span class="metric-label">Utilization</span>
                    <span class="metric-value" id="disk">--%</span>
                </div>
            </div>
            <div class="card">
                <h3>Projects</h3>
                <div class="metric">
                    <span class="metric-label">Active</span>
                    <span class="metric-value" id="projects">-</span>
                </div>
            </div>
        </div>
        
        <!-- CORE SERVICES -->
        <div class="grid-2">
            <div class="card">
                <h3>🔧 Core Services</h3>
                <div id="services-list">Loading...</div>
            </div>
            
            <div class="card">
                <h3>📊 System Status</h3>
                <div id="system-status">Loading...</div>
            </div>
        </div>
        
        <!-- EXTENSION PORTS -->
        <div class="card">
            <h3>📦 Extension Ports (163 Available)</h3>
            <div class="port-grid" id="port-status">Loading...</div>
        </div>
        
        <!-- ALERTS -->
        <div id="alerts-container"></div>
        
        <!-- ACTIONS -->
        <div class="card">
            <h3>⚙️ System Controls</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                <button class="btn" onclick="restartService('master')">Restart Master</button>
                <button class="btn" onclick="restartService('dashboard')">Restart Dashboard</button>
                <button class="btn" onclick="viewLogs('master')">View Master Logs</button>
                <button class="btn" onclick="viewLogs('dashboard')">View Dashboard Logs</button>
            </div>
        </div>
    </div>
    
    <footer>
        <p>SystemAI Enterprise Control Plane | Real-time Monitoring & Management</p>
        <p>Deployment: 2026-04-06 | All Systems Operational ✅</p>
    </footer>
    
    <script>
        const API_URL = 'http://127.0.0.1:50000/api';
        
        function updateDashboard() {
            fetch(API_URL + '/system/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('cpu').textContent = data.metrics.cpu_percent.toFixed(1) + '%';
                    document.getElementById('memory').textContent = data.metrics.memory_percent.toFixed(1) + '%';
                    document.getElementById('disk').textContent = data.metrics.disk_percent.toFixed(1) + '%';
                    document.getElementById('update-time').textContent = new Date().toLocaleTimeString();
                });
            
            fetch(API_URL + '/services/status')
                .then(r => r.json())
                .then(data => {
                    let html = '';
                    for (let [service, status] of Object.entries(data)) {
                        const icon = status === 'running' ? '✅' : status === 'warning' ? '⚠️' : '❌';
                        html += `<div class="service-item">
                            <span>${icon} ${service}</span>
                            <span class="service-status">${status}</span>
                        </div>`;
                    }
                    document.getElementById('services-list').innerHTML = html;
                });
            
            fetch(API_URL + '/projects/summary')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('projects').textContent = data.count || 0;
                });
        }
        
        function restartService(service) {
            if (confirm(`Restart ${service}? This may cause brief downtime.`)) {
                fetch(API_URL + `/control/restart`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({service})
                })
                .then(r => r.json())
                .then(data => alert('Service restarting...'));
            }
        }
        
        function viewLogs(service) {
            window.open(`/logs/${service}`, '_blank');
        }
        
        // Update every 5 seconds
        updateDashboard();
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
'''

# ============ API ENDPOINTS ============

@app.route('/')
def dashboard():
    return render_template_string(ENTERPRISE_HTML)

@app.route('/api/system/status')
def system_status():
    metrics = control_plane.get_system_metrics()
    services = control_plane.get_all_services_status()
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics,
        'services': services
    })

@app.route('/api/services/status')
def services_status():
    return jsonify(control_plane.get_all_services_status())

@app.route('/api/projects/summary')
def projects_summary():
    return jsonify(control_plane.get_projects_summary())

@app.route('/api/control/restart', methods=['POST'])
def control_restart():
    data = request.json
    service = data.get('service', 'all')
    result = control_plane.control_service('restart', service)
    return jsonify(result)

@app.route('/logs/<service>')
def view_logs(service):
    log_file = f'/var/log/systemai-{service}.log'
    try:
        with open(log_file, 'r') as f:
            logs = f.read()
        return f'<pre>{logs}</pre>'
    except:
        return 'Log file not found'

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 SYSTEMAI ENTERPRISE CONTROL PLANE")
    print("=" * 70)
    print(f"Starting on 127.0.0.1:50001 (NGINX reverse proxy to 50000)")
    print(f"Dashboard: http://ip-172-31-26-220:50000/")
    print("=" * 70 + "\n")
    
    app.run(host='127.0.0.1', port=50001, debug=False, threaded=True)
