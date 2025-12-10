"""
Check how Meenakshi Nigam's messages were parsed in December timeline
"""
import json

# Load timeline
with open('src/frontend/public/timeline_dec2025.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find all messages from Meenakshi Nigam
meenakshi_msgs = []
for day in data:
    for m in day['messages']:
        if 'Meenakshi' in m.get('sender', ''):
            meenakshi_msgs.append({
                'date': day['date'],
                'type': m.get('type'),
                'sender': m.get('sender'),
                'time': m.get('time'),
                'length': len(m.get('content', '')),
                'preview': m.get('content', '')[:100]
            })

print(f"Total messages from Meenakshi Nigam: {len(meenakshi_msgs)}\n")

for i, m in enumerate(meenakshi_msgs, 1):
    print(f"{i}. {m['date']} at {m['time']}")
    print(f"   Type: {m['type']}, Length: {m['length']} chars")
    print(f"   Preview: {m['preview']}...")
    print()

# Check for the "FIVE PILLARS" message specifically
five_pillars = [m for m in meenakshi_msgs if 'FIVE PILLARS' in m['preview'] or 'five pillars' in m['preview'].lower()]
print(f"\nMessages containing 'FIVE PILLARS': {len(five_pillars)}")
if five_pillars:
    for m in five_pillars:
        print(f"  - {m['date']}: {m['length']} chars")
