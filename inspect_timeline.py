import json

def inspect_timeline():
    with open('src/frontend/public/timeline.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    image_count = 0
    transcript_count = 0
    
    for day in data:
        for msg in day['messages']:
            if msg.get('type') == 'image':
                image_count += 1
                if image_count <= 5:
                    print(f"Image msg found: {msg}")
            if msg.get('type') == 'transcript':
                transcript_count += 1
                if transcript_count <= 5:
                    print(f"Transcript msg found: {msg}")

    print(f"Total image messages: {image_count}")
    print(f"Total transcript messages: {transcript_count}")

if __name__ == "__main__":
    inspect_timeline()
