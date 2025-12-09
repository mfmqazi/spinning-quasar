
import json
import re

# Paths
timeline_path = "src/frontend/public/timeline.json"
transcripts_path = "youtube_transcripts.txt"

# 1. Load Timeline
try:
    with open(timeline_path, 'r', encoding='utf-8') as f:
        timeline = json.load(f)
except FileNotFoundError:
    print("timeline.json not found.")
    timeline = []

timeline_video_ids = set()
timeline_transcripts = {}

print(f"Loaded {len(timeline)} days from timeline.")

# Collect videos and transcripts from timeline
for day in timeline:
    for msg in day['messages']:
        # Check for video URL
        if msg.get('video_url'):
            vid_match = re.search(r'(?:v=|youtu\.be/|embed/)([\w\-]+)', msg['video_url'])
            if vid_match:
                vid_id = vid_match.group(1)
                timeline_video_ids.add(vid_id)
        
        # Check for transcript
        if msg.get('type') == 'transcript':
            # Try to find which video this transcript belongs to
            # The parser doesn't explicitly link them in the final JSON structure except by proximity or content
            # But let's check the content for "Source URL" which my parser inserts
            content = msg.get('content', '')
            url_match = re.search(r'Source URL:.*(?:v=|youtu\.be/|embed/)([\w\-]+)', content)
            if url_match:
                tid = url_match.group(1)
                timeline_transcripts[tid] = True

# 2. Load Raw Transcripts
raw_transcript_ids = set()
try:
    with open(transcripts_path, 'r', encoding='utf-8') as f:
        content = f.read()
        sections = content.split('================================================================')
        for section in sections:
            url_match = re.search(r'URL:\s*https?://.*(?:v=|youtu\.be/|embed/)([\w\-]+)', section)
            if url_match:
                raw_transcript_ids.add(url_match.group(1))
except FileNotFoundError:
    print("youtube_transcripts.txt not found.")

print(f"Found {len(raw_transcript_ids)} transcripts in raw file.")
print(f"Found {len(timeline_video_ids)} videos in timeline.")
print(f"Found {len(timeline_transcripts)} linked transcripts in timeline.")

# 3. Compare
missing_in_timeline = raw_transcript_ids - timeline_video_ids
print("\n--- Transcripts present in file but Video NOT found in Timeline (Orphaned Transcripts) ---")
for vid in missing_in_timeline:
    print(f"Video ID: {vid}")

missing_transcript_attachment = raw_transcript_ids - set(timeline_transcripts.keys())
print("\n--- Transcripts present in file but NOT linked as Transcript object in Timeline ---")
count = 0
for vid in missing_transcript_attachment:
    print(f"Video ID: {vid}")
    count += 1
    if count > 10:
        print("... and more")
        break

# check if linked transcripts are actually in the timeline videos
unmatched_videos = timeline_video_ids - raw_transcript_ids
print("\n--- Videos in Timeline that have NO transcript in raw file ---")
count = 0
for vid in unmatched_videos:
    print(f"Video ID: {vid}")
    count += 1
    if count > 10:
        print("... and more")
        break
