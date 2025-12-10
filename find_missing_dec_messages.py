"""
Compare raw chat file with parsed timeline to find missing messages
"""
import json
import re

# Read raw chat
with open('Dec 25 Batch/_chat.txt', 'r', encoding='utf-8') as f:
    raw_content = f.read()

# Read parsed timeline
with open('src/frontend/public/timeline_dec2025.json', 'r', encoding='utf-8') as f:
    timeline = json.load(f)

# Extract all message start lines from raw chat
line_pattern = re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}\s*[APap][Mm])\]\s*(.*?):\s*(.*)$', re.MULTILINE)
raw_messages = line_pattern.findall(raw_content)

print(f"Raw chat messages: {len(raw_messages)}")

# Filter out system messages
actual_raw_messages = []
for date_str, time_str, sender, content in raw_messages:
    lower_content = content.lower()
    is_system = (
        "joined using" in lower_content or
        "security code changed" in lower_content or
        "created this group" in lower_content or
        "end-to-end encrypted" in lower_content or
        (lower_content.strip() == "left")
    )
    
    if not is_system:
        actual_raw_messages.append((date_str, time_str, sender, content[:100]))

print(f"Non-system raw messages: {len(actual_raw_messages)}")

# Count parsed messages
parsed_count = sum(len(day['messages']) for day in timeline)
print(f"Parsed messages in timeline: {parsed_count}")

# Show first few non-system messages from raw chat
print("\nFirst 10 non-system messages from raw chat:")
for i, (date, time, sender, preview) in enumerate(actual_raw_messages[:10], 1):
    print(f"{i}. [{date}, {time}] {sender}: {preview}...")

# Check if all these are in the parsed timeline
print("\nChecking if these messages are in the parsed timeline...")
parsed_senders = [m['sender'] for day in timeline for m in day['messages']]
for i, (date, time, sender, preview) in enumerate(actual_raw_messages[:10], 1):
    if sender in parsed_senders:
        print(f"  ✓ Message {i} found")
    else:
        print(f"  ✗ Message {i} MISSING: {sender}")
