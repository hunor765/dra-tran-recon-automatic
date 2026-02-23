import json
import sys

def analyze_logs(filename):
    with open(filename) as f:
        data = json.load(f)
    
    print(f"Total log entries: {len(data)}\n")
    print("="*80)
    print("AUTH-RELATED LOGS (last 50)\n")
    print("="*80)
    
    auth_logs = []
    for entry in data:
        msg = entry.get('message', '')
        logger = entry.get('attributes', {}).get('logger', '')
        if 'core.auth' in logger or 'token' in msg.lower() or 'jwks' in msg.lower() or 'auth' in msg.lower() or 'validat' in msg.lower():
            auth_logs.append(entry)
    
    for entry in auth_logs[-50:]:
        ts = entry['timestamp'][:19].replace('T', ' ')
        msg = entry['message'][:120]
        level = entry.get('attributes', {}).get('level', 'info')
        print(f"{ts} [{level.upper():5}] {msg}")

if __name__ == '__main__':
    analyze_logs('logs.1771841151347.json')
