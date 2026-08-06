"""Kill the backend server on port 8000 and restart it"""
import subprocess, time, os, sys

# Find PID on port 8000
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
lines = [l for l in result.stdout.splitlines() if ':8000' in l and 'LISTENING' in l]
print(f"Found {len(lines)} listeners on port 8000")

for l in lines:
    parts = l.split()
    pid = parts[-1]
    print(f"Killing PID {pid}")
    r = subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, text=True)
    print(f"  Result: {r.stdout.strip()} {r.stderr.strip()}")

time.sleep(3)

# Verify port is free
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
lines = [l for l in result.stdout.splitlines() if ':8000' in l and 'LISTENING' in l]
print(f"Port 8000 still listening: {len(lines) > 0}")

if len(lines) > 0:
    print("WARNING: Port still in use. Trying to kill all python processes...")
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
    print(result.stdout[:2000])