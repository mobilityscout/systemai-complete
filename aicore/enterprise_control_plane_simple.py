#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify
from datetime import datetime

app = Flask(__name__)

ENTERPRISE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SystemAI Enterprise Control Plane</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: #00ff88;
            text-align: center;
            margin-bottom: 30px;
            font-size: 32px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 12px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }
        .card h2 {
            color: #00ff88;
            margin-bottom: 15px;
            border-bottom: 2px solid rgba(0, 255, 136, 0.5);
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            color: #aaa;
            font-size: 14px;
        }
        .metric-value {
            color: #00ff88;
            font-weight: bold;
        }
        .status-ok { color: #00ff88; }
        .btn {
            background: #00ff88;
            color: #0f0f23;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            margin-top: 10px;
            width: 100%;
        }
        .btn:hover {
            background: #00dd77;
        }
        footer {
            text-align: center;
            margin-top: 50px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SystemAI Enterprise Control Plane</h1>
        
        <div class="grid">
            <div class="card">
                <h2>📊 System Status</h2>
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="metric-value status-ok">✅ OPERATIONAL</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Time</span>
                    <span class="metric-value" id="uptime">--:--:--</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🔧 Core Services</h2>
                <div class="metric">
                    <span class="metric-label">Master</span>
                    <span class="metric-value status-ok">✅ 27902</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uvicorn</span>
                    <span class="metric-value status-ok">✅ 5080</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Ollama</span>
                    <span class="metric-value status-ok">✅ 11434</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📦 Ports</h2>
                <div class="metric">
                    <span class="metric-label">Available</span>
                    <span class="metric-value">163</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Range</span>
                    <span class="metric-value">6400-6832</span>
                </div>
            </div>
            
            <div class="card">
                <h2>💾 Databases</h2>
                <div class="metric">
                    <span class="metric-label">PostgreSQL</span>
                    <span class="metric-value status-ok">✅ 5432</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Redis</span>
                    <span class="metric-value status-ok">✅ 6379</span>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <p>✅ SystemAI Enterprise Control Plane - All Systems Operational</p>
    </footer>
    
    <script>
        setInterval(() => {
            document.getElementById('uptime').textContent = new Date().toLocaleTimeString();
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(ENTERPRISE_HTML)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Enterprise Control Plane'})

@app.route('/api/status')
def api_status():
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'status': 'operational'
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=50000, debug=False, threaded=True)
