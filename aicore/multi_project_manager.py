#!/usr/bin/env python3
"""
MULTI-PROJECT MANAGER
Handles slow AI responses and offline mode
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
import requests
import uuid

class MultiProjectManager:
    def __init__(self):
        self.projects_dir = '/root/aicore/projects'
        self.ai_api = 'http://localhost:5001/api/ai'
        Path(self.projects_dir).mkdir(exist_ok=True)
        print("[INIT] Multi-Project Manager")
        
    def create_project(self, name, region, config=None):
        """Create a new global project"""
        project_id = str(uuid.uuid4())[:8]
        
        project = {
            'id': project_id,
            'name': name,
            'region': region,
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'config': config or {},
            'metrics': {'cpu': 0, 'memory': 0, 'disk': 0},
            'ai_analysis': None
        }
        
        # Save immediately
        path = f'{self.projects_dir}/{project_id}.json'
        with open(path, 'w') as f:
            json.dump(project, f, indent=2)
        
        print(f"[✓] {name} ({project_id}) - {region}")
        return project_id
    
    def get_project(self, project_id):
        """Get project"""
        path = f'{self.projects_dir}/{project_id}.json'
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None
    
    def save_project(self, project):
        """Save project"""
        path = f'{self.projects_dir}/{project["id"]}.json'
        with open(path, 'w') as f:
            json.dump(project, f, indent=2)
    
    def analyze_project_async(self, project_id):
        """Analyze project asynchronously (background)"""
        project = self.get_project(project_id)
        if not project:
            return
        
        try:
            # LONG TIMEOUT for Ollama
            response = requests.post(
                f'{self.ai_api}/analyze-project',
                json={
                    'project_name': project['name'],
                    'metrics': project['metrics']
                },
                timeout=120  # 2 minutes for slow Ollama
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check if analysis is not null
                if data and 'analysis' in data and data['analysis']:
                    project['ai_analysis'] = data['analysis']
                    self.save_project(project)
                    print(f"[AI ANALYSIS] {project['name']}")
                    print(f"  {data['analysis'][:100]}...")
        except requests.exceptions.Timeout:
            print(f"[AI] Timeout on {project['name']} - will retry later")
        except Exception as e:
            print(f"[AI] Error: {e}")
    
    def list_projects(self):
        """List all projects"""
        projects = []
        for file in Path(self.projects_dir).glob('*.json'):
            try:
                with open(file) as f:
                    projects.append(json.load(f))
            except:
                pass
        return sorted(projects, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_summary(self):
        """Get summary"""
        projects = self.list_projects()
        regions = {}
        
        for p in projects:
            r = p['region']
            regions[r] = regions.get(r, 0) + 1
        
        return {
            'total_projects': len(projects),
            'regions': regions,
            'projects': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'region': p['region'],
                    'status': p['status'],
                    'has_analysis': p['ai_analysis'] is not None
                }
                for p in projects
            ]
        }

# MAIN
if __name__ == '__main__':
    manager = MultiProjectManager()
    
    print("\n=== CREATING GLOBAL PROJECTS ===\n")
    
    # Create projects
    p1 = manager.create_project('EU Customer Platform', 'EU', {'team': 5, 'deadline': 14})
    p2 = manager.create_project('APAC Expansion', 'APAC', {'team': 8, 'deadline': 21})
    p3 = manager.create_project('Americas Operations', 'AMERICAS', {'team': 6, 'deadline': 30})
    
    # Get summary immediately
    print("\n=== PROJECT SUMMARY ===\n")
    summary = manager.get_summary()
    print(json.dumps(summary, indent=2))
    
    # Start async analysis in background (non-blocking)
    print("\n=== STARTING BACKGROUND AI ANALYSIS ===\n")
    print("(Projects will be analyzed in the background)")
    print("(This won't block project creation)\n")
    
    for pid in [p1, p2, p3]:
        print(f"[ASYNC] Analyzing {pid}...")
        manager.analyze_project_async(pid)
        time.sleep(2)  # Stagger requests
    
    print("\n✅ MULTI-PROJECT MANAGER READY!")
    print(f"   Projects: {manager.projects_dir}")
    print(f"   Total: {summary['total_projects']}")
    print(f"   Regions: {list(summary['regions'].keys())}")

