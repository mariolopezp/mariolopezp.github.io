import sys
import subprocess

param = '-n' if sys.platform.startswith('win') else '-c'
hostname = "google.com"

def perform_task_ping():
    print("Ping task started")
    
    response = subprocess.run(["ping", param, "1", hostname])
    
    if response.returncode == 0:
        print(f"{hostname} is up!")
    else:
        print(f"{hostname} is down!")