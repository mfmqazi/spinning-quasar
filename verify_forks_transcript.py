import json

# Load timeline data
with open('src/frontend/public/timeline.json', encoding='utf-8') as f:
    data = json.load(f)

# Find all messages related to the Forks Over Knives video
video_id = '5B8zyQ0oeGQ'
related_messages = []

for day in data:
    for msg in day['messages']:
        video_url = msg.get('video_url', '')
        if video_id in str(video_url):
            related_messages.append({
                'type': msg.get('type'),
                'sender': msg.get('sender'),
                'has_transcript': 'transcript' in msg.get('content', '').lower() or msg.get('type') == 'transcript',
                'content_length': len(msg.get('content', ''))
            })

print(f"Found {len(related_messages)} messages related to Forks Over Knives video ({video_id})")
print("\nMessage breakdown:")
for i, msg in enumerate(related_messages, 1):
    print(f"{i}. Type: {msg['type']}, Sender: {msg['sender']}, Content Length: {msg['content_length']}, Has Transcript: {msg['has_transcript']}")

# Count transcripts specifically
transcript_count = sum(1 for msg in related_messages if msg['type'] == 'transcript')
print(f"\n✓ Total transcript entries: {transcript_count}")

if transcript_count > 0:
    print("✓ Forks Over Knives transcript successfully integrated!")
else:
    print("⚠ No transcript entries found - may need to regenerate timeline")
