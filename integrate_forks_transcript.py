"""
Script to integrate the Forks Over Knives transcript into the application.
This reads the transcript from 'Forks Over Knives.txt' and appends it to
youtube_transcripts.txt and chat_backup.txt in the proper format.
"""

import os

def clean_transcript_text(raw_text):
    """
    Clean the transcript text by removing timestamps and formatting.
    """
    lines = raw_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip header lines and empty lines
        if not line or line.startswith('#') or line.startswith('http'):
            continue
        
        # Remove timestamp prefix (e.g., "00:00:17.250")
        if line and len(line) > 12 and line[2] == ':' and line[5] == ':':
            # This line has a timestamp, extract text after it
            parts = line.split(' ', 1)
            if len(parts) > 1:
                cleaned_lines.append(parts[1])
        else:
            cleaned_lines.append(line)
    
    return ' '.join(cleaned_lines)

def main():
    transcript_file = "Forks Over Knives.txt"
    video_id = "5B8zyQ0oeGQ"
    video_title = "Forks Over Knives"
    video_url = f"https://youtu.be/{video_id}"
    
    # Read the transcript
    print(f"Reading transcript from {transcript_file}...")
    with open(transcript_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    # Clean the transcript
    print("Cleaning transcript text...")
    cleaned_text = clean_transcript_text(raw_text)
    
    # Format the entry
    entry = f"\n\n================================================================\n"
    entry += f"[Video Transcript] {video_title}\n"
    entry += f"URL: {video_url}\n"
    entry += f"================================================================\n"
    entry += f"{cleaned_text}\n"
    
    # Append to youtube_transcripts.txt
    print("Appending to youtube_transcripts.txt...")
    with open("youtube_transcripts.txt", "a", encoding="utf-8") as f:
        f.write(entry)
    
    # Append to chat_backup.txt
    print("Appending to chat_backup.txt...")
    with open("chat_backup.txt", "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"✓ Successfully integrated {video_title} transcript!")
    print(f"  - Added to youtube_transcripts.txt")
    print(f"  - Added to chat_backup.txt")
    print(f"  - Transcript length: {len(cleaned_text)} characters")

if __name__ == "__main__":
    main()
