"""
Check messages on 12/08/2025 to find the FIVE PILLARS messages
"""
import json

# Load timeline
with open('src/frontend/public/timeline_dec2025.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find 12/08/2025
day = [d for d in data if d['date'] == '12/08/2025'][0]

print(f"Messages on 12/08/2025: {len(day['messages'])}\n")

# Look for messages from Meenakshi Nigam
meenakshi_msgs = [m for m in day['messages'] if 'Meenakshi' in m.get('sender', '')]

print(f"Messages from Meenakshi Nigam on 12/08: {len(meenakshi_msgs)}\n")

for i, m in enumerate(meenakshi_msgs, 1):
    print(f"{i}. Type: {m.get('type')}")
    print(f"   Time: {m.get('time')}")
    print(f"   Length: {len(m.get('content', ''))} chars")
    content = m.get('content', '')
    if 'FIVE PILLARS' in content:
        print(f"   ✓ Contains 'FIVE PILLARS'")
    if 'First Pillar' in content:
        print(f"   ✓ Contains 'First Pillar'")
    print(f"   Preview: {content[:100]}...")
    print()

# Check if there are 2 separate messages with these contents
five_pillars_msg = [m for m in meenakshi_msgs if 'FIVE PILLARS OF HEALTH' in m.get('content', '')]
first_pillar_msg = [m for m in meenakshi_msgs if 'First Pillar of Health' in m.get('content', '') and 'FIVE PILLARS' not in m.get('content', '')]

print(f"\nMessages with 'FIVE PILLARS OF HEALTH': {len(five_pillars_msg)}")
print(f"Messages with 'First Pillar of Health' (separate): {len(first_pillar_msg)}")

if len(five_pillars_msg) > 0:
    print(f"\nFIVE PILLARS message length: {len(five_pillars_msg[0]['content'])} chars")
    print(f"Contains 'First Pillar': {'First Pillar' in five_pillars_msg[0]['content']}")
