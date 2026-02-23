import json

with open("logs.1771845654873.json") as f:
    data = json.load(f)

print("=== ERROR SUMMARY (Last 300 logs) ===\n")

errors_found = []
for entry in data[-300:]:
    msg = entry.get("message", "")
    level = entry.get("attributes", {}).get("level", "info")
    logger = entry.get("attributes", {}).get("logger", "")
    
    # Look for actual error content
    if level in ["error", "warning"] or "Error" in msg:
        # Skip stack trace intermediate lines
        if any(x in msg for x in ['File "/usr/local/lib', "await self.", "raise e", "async def"]):
            continue
        errors_found.append({
            "level": level,
            "logger": logger,
            "msg": msg[:300]
        })

# Print unique errors
seen = set()
for err in errors_found:
    key = err["msg"][:100]
    if key not in seen:
        seen.add(key)
        print(f"[{err['level'].upper()}] {err['logger']}")
        print(f"  {err['msg']}")
        print()
