#!/usr/bin/env python3
import sys
import time
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/aicore')
sys.path.insert(0, '/root/system_root')

def main():
    print("[SYSTEM] Starting Enhanced AI Core with Port Monitoring...", flush=True)
    
    try:
        from port_monitor import SystemAIWithPortMonitoring
        system_monitor = SystemAIWithPortMonitoring()
        print("[OK] Port Monitor loaded", flush=True)
    except Exception as e:
        print(f"[WARN] Port Monitor: {e}", flush=True)
        system_monitor = None
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            current_time = time.time()
            
            if iteration % 10 == 0:
                timestamp = datetime.now().isoformat()
                print(f"[LOOP {iteration}] {timestamp}", flush=True)
                
                if system_monitor:
                    port_status = system_monitor.check_ports_if_needed(current_time)
                    if port_status:
                        summary = system_monitor.port_monitor.get_status_summary(port_status)
                        print(summary, flush=True)
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[SYSTEM] Stopped", flush=True)
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
