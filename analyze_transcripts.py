import json

# Load timeline data
with open('src/frontend/public/timeline.json', encoding='utf-8') as f:
    data = json.load(f)

# Find transcript entries for Forks Over Knives
transcripts = [m for day in data for m in day['messages'] 
               if m.get('type') == 'transcript' and '5B8zyQ0oeGQ' in str(m.get('video_url', ''))]

print(f"Found {len(transcripts)} transcript(s) for Forks Over Knives\n")

for i, t in enumerate(transcripts, 1):
    print(f"Transcript {i}:")
    print(f"  Content length: {len(t['content'])} characters")
    print(f"  Content preview: {t['content'][:100]}")
    print(f"  video_url: {t.get('video_url')}")
    print()

# Find the video messages
video_msgs = [m for day in data for m in day['messages'] 
              if m.get('video_url') and '5B8zyQ0oeGQ' in str(m.get('video_url', ''))]

print(f"\nFound {len(video_msgs)} video message(s):")
for i, v in enumerate(video_msgs, 1):
    print(f"Video {i}: type={v.get('type')}, sender={v.get('sender')}, video_url={v.get('video_url')}")
