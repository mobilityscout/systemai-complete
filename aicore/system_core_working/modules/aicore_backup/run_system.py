import sys
import os

sys.path.append("/root")

from aicore.core_health import CoreHealth
from aicore.core_repair import CoreRepair

health = CoreHealth()
repair = CoreRepair()

# 🔴 CORE CHECK (VOR ALLEM)
issues = health.scan()

if issues:

    print({"core_issues": issues})

    for i in issues:
        fix = repair.repair(i["file"])
        print({"core_repair": fix})

# 🔴 ERST DANACH AI START
from aicore.system_entry import SystemEntry

system = SystemEntry("t1")

print("AI CORE (GOVERNED MODE)")

while True:

    events = system.ai.tick()

    for e in events:
        print({"immune": e})

    user_input = input(">> ")

    if user_input.startswith("!"):
        os.system(user_input[1:])
        continue

    result = system.handle(user_input)

    print(result)
