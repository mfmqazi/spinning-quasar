import json

def verify_timeline():
    with open('src/frontend/public/timeline.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    transcript_count = 0
    sample_content = None
    
    for day in data:
        for msg in day['messages']:
            if msg.get('type') == 'transcript':
                transcript_count += 1
                if not sample_content:
                    sample_content = msg.get('content')
                    print(f"Sample Transcript Content: {sample_content[:200]}...")

    print(f"Total transcripts found in json: {transcript_count}")

if __name__ == "__main__":
    verify_timeline()
