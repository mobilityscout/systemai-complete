#!/usr/bin/env python3
import sys
import os
import time

sys.path.insert(0, '/root/aicore')
sys.path.insert(0, '/root')

def main():
    print("[SYSTEM] AI Core System Starting...")
    iteration = 0
    
    try:
        while True:
            iteration += 1
            if iteration % 10 == 0:
                print(f"[LOOP] Iteration {iteration}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[SYSTEM] Stopped")
    except Exception as e:
        print(f"[ERROR] {e}")
        return 2
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
