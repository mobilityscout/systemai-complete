import sys
sys.path.append("/root")
sys.path.append("/root/aicore")

from aicore.system_entry import SystemEntry

system = SystemEntry("t1")

print("AI CORE (FINAL MODE)")

while True:
    user_input = input(">> ")
    result = system.handle(user_input)
    print(result)
