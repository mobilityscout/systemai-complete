#!/usr/bin/env python3
"""
DEVELOPER CHAT UI
Beautiful interface for system developer
"""

from flask import Flask, render_template_string

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI System Developer Chat</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background: #0d1117;
            color: #c9d1d9;
            height: 100vh;
            display: flex;
        }
        
        .sidebar {
            width: 300px;
            background: #010409;
            border-right: 1px solid #30363d;
            padding: 20px;
            overflow-y: auto;
        }
        
        .sidebar h3 { color: #58a6ff; margin-bottom: 15px; }
        
        .sidebar-section {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #30363d;
        }
        
        .sidebar-item {
            padding: 8px 12px;
            margin: 5px 0;
            background: #161b22;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9em;
        }
        
        .sidebar-item:hover {
            background: #21262d;
            color: #58a6ff;
        }
        
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            padding: 20px;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 { color: #58a6ff; font-size: 1.5em; }
        
        .status-indicator {
            display: flex;
            gap: 10px;
        }
        
        .status-item {
            background: #161b22;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.85em;
        }
        
        .status-online { color: #3fb950; }
        .status-offline { color: #f85149; }
        
        .chat-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 8px;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.dev {
            background: #161b22;
            border-left: 3px solid #58a6ff;
        }
        
        .message.system {
            background: #0d3d1f;
            border-left: 3px solid #3fb950;
        }
        
        .message.error {
            background: #3d1f1f;
            border-left: 3px solid #f85149;
        }
        
        .message-time {
            font-size: 0.8em;
            opacity: 0.6;
            margin-bottom: 5px;
        }
        
        .message-content {
            word-wrap: break-word;
            font-size: 0.95em;
        }
        
        .code-block {
            background: #010409;
            padding: 10px;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 0.9em;
            overflow-x: auto;
        }
        
        .input-area {
            background: #161b22;
            padding: 15px;
            border-top: 1px solid #30363d;
            display: flex;
            gap: 10px;
        }
        
        input {
            flex: 1;
            background: #0d1117;
            border: 1px solid #30363d;
            color: #c9d1d9;
            padding: 10px;
            border-radius: 6px;
            font-family: inherit;
        }
        
        input:focus {
            outline: none;
            border-color: #58a6ff;
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
        }
        
        button {
            background: #238636;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }
        
        button:hover {
            background: #2ea043;
        }
        
        .autocomplete {
            position: absolute;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
            min-width: 200px;
        }
        
        .autocomplete-item {
            padding: 8px 12px;
            cursor: pointer;
            font-size: 0.9em;
        }
        
        .autocomplete-item:hover {
            background: #21262d;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>🧠 System Developer</h3>
        
        <div class="sidebar-section">
            <h4 style="color: #79c0ff; font-size: 0.9em;">Quick Commands</h4>
            <div class="sidebar-item" onclick="sendCommand('/status')">/status</div>
            <div class="sidebar-item" onclick="sendCommand('/projects')">/projects</div>
            <div class="sidebar-item" onclick="sendCommand('/workers')">/workers</div>
            <div class="sidebar-item" onclick="sendCommand('/metrics')">/metrics</div>
        </div>
        
        <div class="sidebar-section">
            <h4 style="color: #79c0ff; font-size: 0.9em;">Knowledge</h4>
            <div class="sidebar-item" onclick="sendCommand('/knowledge')">/knowledge</div>
            <div class="sidebar-item" onclick="sendCommand('/memory')">/memory</div>
            <div class="sidebar-item" onclick="sendCommand('/logs 50')">/logs</div>
        </div>
        
        <div class="sidebar-section">
            <h4 style="color: #79c0ff; font-size: 0.9em;">Help</h4>
            <div class="sidebar-item" onclick="sendCommand('/help')">/help</div>
        </div>
    </div>
    
    <div class="main">
        <div class="header">
            <h1>💻 AI System Developer Chat</h1>
            <div class="status-indicator" id="status-indicator">
                <div class="status-item">System Status: <span class="status-online">ONLINE</span></div>
            </div>
        </div>
        
        <div class="chat-area" id="chat"></div>
        
        <div class="input-area">
            <input 
                type="text" 
                id="command-input" 
                placeholder="Enter command... (type /help for available commands)"
                autocomplete="off"
            >
            <button onclick="executeCommand()">Send</button>
        </div>
    </div>
    
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('command-input');
        
        // Add initial message
        addMessage('System ready. Type /help for available commands.', 'system');
        
        function addMessage(text, type = 'dev') {
            const time = new Date().toLocaleTimeString();
            const msg = document.createElement('div');
            msg.className = `message ${type}`;
            msg.innerHTML = `
                <div class="message-time">${time}</div>
                <div class="message-content">${escapeHtml(text)}</div>
            `;
            chat.appendChild(msg);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function sendCommand(cmd) {
            input.value = cmd;
            executeCommand();
        }
        
        async function executeCommand() {
            const command = input.value.trim();
            if (!command) return;
            
            addMessage(`> ${command}`, 'dev');
            input.value = '';
            
            try {
                const response = await fetch('http://localhost:5091/api/dev/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage(`ERROR: ${data.error}`, 'error');
                } else {
                    addMessage(JSON.stringify(data, null, 2), 'system');
                }
            } catch (e) {
                addMessage(`CONNECTION ERROR: ${e.message}`, 'error');
            }
        }
        
        input.addEventListener('keypress', e => {
            if (e.key === 'Enter') executeCommand();
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def dev_chat():
    return render_template_string(HTML)

if __name__ == '__main__':
    print("[DEVELOPER CHAT UI] Starting on port 5090...")
    app.run(host='0.0.0.0', port=5090, debug=False)

