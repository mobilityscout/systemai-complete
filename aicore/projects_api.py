#!/usr/bin/env python3
"""
PROJECTS REST API
Manage multi-project system via HTTP
"""

from flask import Flask, request, jsonify
from multi_project_manager import MultiProjectManager
from datetime import datetime
import json

app = Flask(__name__)
manager = MultiProjectManager()

# ============ PROJECT ENDPOINTS ============

@app.route('/api/projects/create', methods=['POST'])
def create_project():
    """Create new project"""
    data = request.json or {}
    name = data.get('name')
    region = data.get('region')
    config = data.get('config', {})
    
    if not name or not region:
        return jsonify({'error': 'Missing name or region'}), 400
    
    project_id = manager.create_project(name, region, config)
    return jsonify({'project_id': project_id, 'status': 'created'})

@app.route('/api/projects/list', methods=['GET'])
def list_projects():
    """List all projects"""
    projects = manager.list_projects()
    return jsonify({
        'total': len(projects),
        'projects': projects
    })

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get specific project"""
    project = manager.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project)

@app.route('/api/projects/<project_id>/analyze', methods=['POST'])
def analyze_project(project_id):
    """Trigger AI analysis for project"""
    project = manager.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Trigger async analysis
    manager.analyze_project_async(project_id)
    
    return jsonify({
        'project_id': project_id,
        'status': 'analysis_started'
    })

@app.route('/api/projects/by-region/<region>', methods=['GET'])
def projects_by_region(region):
    """Get projects in region"""
    projects = manager.list_projects()
    filtered = [p for p in projects if p['region'] == region]
    return jsonify({
        'region': region,
        'count': len(filtered),
        'projects': filtered
    })

@app.route('/api/projects/summary', methods=['GET'])
def summary():
    """Get global summary"""
    return jsonify(manager.get_summary())

@app.route('/api/projects/health', methods=['GET'])
def health():
    """Health check"""
    projects = manager.list_projects()
    analyzed = sum(1 for p in projects if p['ai_analysis'])
    
    return jsonify({
        'status': 'online',
        'total_projects': len(projects),
        'analyzed': analyzed,
        'pending_analysis': len(projects) - analyzed,
        'timestamp': datetime.now().isoformat()
    })

# ============ STATS ============

@app.route('/api/stats/overview', methods=['GET'])
def stats_overview():
    """Overall statistics"""
    projects = manager.list_projects()
    
    stats = {
        'total_projects': len(projects),
        'by_region': {},
        'by_status': {},
        'analysis_coverage': 0
    }
    
    analyzed_count = 0
    
    for p in projects:
        # By region
        region = p['region']
        stats['by_region'][region] = stats['by_region'].get(region, 0) + 1
        
        # By status
        status = p['status']
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Analysis coverage
        if p['ai_analysis']:
            analyzed_count += 1
    
    if len(projects) > 0:
        stats['analysis_coverage'] = round(100 * analyzed_count / len(projects), 1)
    
    return jsonify(stats)

# ============ ROOT ============

@app.route('/api/projects', methods=['GET'])
def root():
    """API Info"""
    return jsonify({
        'service': 'Multi-Project Manager API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'POST /api/projects/create': 'Create new project',
            'GET /api/projects/list': 'List all projects',
            'GET /api/projects/<id>': 'Get project details',
            'POST /api/projects/<id>/analyze': 'Trigger AI analysis',
            'GET /api/projects/by-region/<region>': 'Get projects in region',
            'GET /api/projects/summary': 'Get global summary',
            'GET /api/projects/health': 'Health check',
            'GET /api/stats/overview': 'Statistics'
        }
    })

if __name__ == '__main__':
    print("[API] Projects API starting on 0.0.0.0:5002")
    app.run(host='0.0.0.0', port=5002, debug=False)


# Add static file serving
from flask import send_file
import os

@app.route('/', methods=['GET'])
def dashboard():
    """Serve dashboard"""
    return send_file('/root/aicore/static/index.html')

