import json

# Load timeline data
with open('src/frontend/public/timeline.json', encoding='utf-8') as f:
    data = json.load(f)

# Find all messages related to the Forks Over Knives video
video_id = '5B8zyQ0oeGQ'
msgs = []

for day in data:
    for m in day['messages']:
        video_url = m.get('video_url', '')
        if video_id in str(video_url):
            msgs.append(m)

print(f"Messages with video_url containing {video_id}:")
print("=" * 80)
for i, m in enumerate(msgs, 1):
    print(f"\n{i}. Type: {m.get('type')}")
    print(f"   Sender: {m.get('sender')}")
    print(f"   video_url: {m.get('video_url')}")
    print(f"   content_len: {len(m.get('content', ''))}")
    if m.get('type') == 'transcript':
        print(f"   content preview: {m.get('content', '')[:100]}...")
