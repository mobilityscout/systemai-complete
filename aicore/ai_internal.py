#!/usr/bin/env python3
"""
INTERNAL AI - ULTRA FAST
Aggressive optimization for speed
"""

from flask import Flask, request, jsonify
import requests
import time
import hashlib
import sqlite3

app = Flask(__name__)
MODEL = 'orca-mini'
CACHE_DB = '/root/aicore/fast_cache.db'

def init_cache():
    if not sqlite3.connect(CACHE_DB).execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='cache'"
    ).fetchone():
        conn = sqlite3.connect(CACHE_DB)
        conn.execute('''CREATE TABLE cache (
            hash TEXT PRIMARY KEY,
            response TEXT
        )''')
        conn.commit()
        conn.close()

def get_cache(q):
    h = hashlib.md5(q.lower().encode()).hexdigest()
    try:
        r = sqlite3.connect(CACHE_DB).execute(
            'SELECT response FROM cache WHERE hash = ?', (h,)
        ).fetchone()
        return r[0] if r else None
    except:
        return None

def set_cache(q, r):
    h = hashlib.md5(q.lower().encode()).hexdigest()
    try:
        conn = sqlite3.connect(CACHE_DB)
        conn.execute('INSERT OR REPLACE INTO cache VALUES (?, ?)', (h, r))
        conn.commit()
        conn.close()
    except:
        pass

@app.route('/api/ai/ask', methods=['POST'])
def ask():
    data = request.json or {}
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({'error': 'No prompt'}), 400
    
    start = time.time()
    
    # CHECK CACHE FIRST - instant!
    cached = get_cache(prompt)
    if cached:
        return jsonify({
            'response': cached,
            'model': MODEL,
            'ms': int((time.time() - start) * 1000),
            'source': 'CACHE'
        })
    
    try:
        # ULTRA SHORT - nur 20 tokens!
        r = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': MODEL,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_predict': 20,        # ← VERY SHORT!
                    'temperature': 0.1,       # ← Deterministic
                    'num_thread': 8,
                    'top_k': 5,              # ← Tiny search space
                    'top_p': 0.2,
                }
            },
            timeout=60
        )
        
        elapsed = time.time() - start
        
        if r.status_code == 200:
            response = r.json().get('response', '').strip()
            
            # Cache for next time
            set_cache(prompt, response)
            
            return jsonify({
                'response': response,
                'model': MODEL,
                'ms': int(elapsed * 1000),
                'source': 'AI'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_cache()
    print(f"[INTERNAL AI] Port 5010 - ULTRA FAST MODE")
    app.run(host='0.0.0.0', port=5010, debug=False, threaded=True)

