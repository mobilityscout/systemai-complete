#!/usr/bin/env python3
import subprocess, json, time
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortMonitor:
    CRITICAL_PORTS = {
        50000: {'name': 'PROJECT_PORT (NGINX)', 'type': 'production'},
        27902: {'name': 'BACKEND (system_loop)', 'type': 'backend'},
        5014: {'name': 'WSGI (gunicorn)', 'type': 'wsgi'},
        5080: {'name': 'UVICORN (labx)', 'type': 'api'},
    }
    
    def __init__(self, log_file='/root/system_root/port_monitor.jsonl'):
        self.log_file = Path(log_file)
        self.status_file = Path('/root/system_root/port_status.json')
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_port_info(self, port):
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                if lines:
                    processes = []
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 11:
                            processes.append({
                                'command': parts[0],
                                'pid': int(parts[1]),
                                'user': parts[2],
                                'state': parts[9],
                                'connection': ' '.join(parts[10:])
                            })
                    return {'status': 'ACTIVE', 'processes': processes}
            return {'status': 'INACTIVE', 'processes': []}
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
    
    def check_all_ports(self):
        status = {'timestamp': datetime.now().isoformat(), 'ports': {}}
        for port, config in self.CRITICAL_PORTS.items():
            info = self.get_port_info(port)
            status['ports'][port] = {
                'config': config,
                'info': info,
                'healthy': info['status'] == 'ACTIVE'
            }
        return status
    
    def log_status(self, status):
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(status) + '\n')
        except Exception as e:
            logger.error(f"Log failed: {e}")
    
    def save_current_status(self, status):
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Save failed: {e}")
    
    def get_status_summary(self, status):
        summary = "\n" + "="*70 + "\n"
        summary += f"PORT MONITOR - {status['timestamp']}\n"
        summary += "="*70 + "\n"
        healthy_count = 0
        for port, data in status['ports'].items():
            name = data['config']['name']
            is_healthy = data['healthy']
            icon = "OK" if is_healthy else "DOWN"
            summary += f"[{icon}] {port:5d} - {name:30s}"
            if is_healthy:
                healthy_count += 1
                processes = data['info']['processes']
                if processes:
                    p = processes[0]
                    summary += f" [PID: {p['pid']}, User: {p['user']}]\n"
                else:
                    summary += " [No process]\n"
            else:
                summary += " [ALERT - DOWN]\n"
        summary += "="*70 + "\n"
        summary += f"Summary: {healthy_count}/{len(self.CRITICAL_PORTS)} ports healthy\n"
        summary += "="*70 + "\n"
        return summary

class SystemAIWithPortMonitoring:
    def __init__(self):
        self.port_monitor = PortMonitor()
        self.last_check = 0
        self.check_interval = 30
    
    def check_ports_if_needed(self, current_time):
        if current_time - self.last_check > self.check_interval:
            status = self.port_monitor.check_all_ports()
            self.port_monitor.log_status(status)
            self.port_monitor.save_current_status(status)
            self.last_check = current_time
            return status
        return None
    
    def get_port_status(self):
        return self.port_monitor.check_all_ports()

if __name__ == '__main__':
    monitor = PortMonitor()
    status = monitor.check_all_ports()
    print(monitor.get_status_summary(status))
    monitor.save_current_status(status)
    monitor.log_status(status)
    print("OK - Port Monitor ready")
