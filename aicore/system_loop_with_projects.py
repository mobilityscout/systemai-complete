#!/usr/bin/env python3
"""
SYSTEM LOOP WITH PROJECTS
Manages projects, analyzes with AI in background
"""

import sys
import time
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/aicore')

def main():
    print("[SYSTEM] AI Core with Project Management Starting...", flush=True)
    
    try:
        from multi_project_manager import MultiProjectManager
        manager = MultiProjectManager()
        print("[✓] Project Manager loaded", flush=True)
    except Exception as e:
        print(f"[!] Project Manager: {e}", flush=True)
        manager = None
    
    iteration = 0
    analysis_queue = []
    
    try:
        while True:
            iteration += 1
            
            if iteration % 10 == 0:
                timestamp = datetime.now().isoformat()
                print(f"\n[LOOP {iteration}] {timestamp}", flush=True)
                
                if manager:
                    projects = manager.list_projects()
                    print(f"[PROJECTS] {len(projects)} active projects", flush=True)
                    
                    # Show project status
                    for p in projects[:5]:
                        status = "analyzed ✓" if p['ai_analysis'] else "pending"
                        print(f"  - {p['name']} ({p['region']}) [{status}]", flush=True)
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[SYSTEM] Stopped", flush=True)
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        return 2
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

