"""
Analyze the December 2025 chat file to see what's being filtered out
"""
import re

# Read the chat file
with open('Dec 25 Batch/_chat.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")

# Pattern for message lines
line_pattern = re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}\s*[APap][Mm])\]\s*(.*?):\s*(.*)$')

total_messages = 0
system_messages = 0
actual_messages = 0

for line in lines:
    line = line.strip()
    match = line_pattern.match(line)
    if match:
        total_messages += 1
        date_str, time_str, sender, msg_content = match.groups()
        
        # Check if it's a system message
        lower_content = msg_content.lower()
        is_system = False
        
        if "joined using" in lower_content:
            is_system = True
        elif "security code changed" in lower_content:
            is_system = True
        elif "added" in lower_content and (re.search(r'added\s+[\+~]', msg_content) or "added you" in lower_content):
            is_system = True
        elif lower_content.strip() == "left":
            is_system = True
        
        if is_system:
            system_messages += 1
        else:
            actual_messages += 1

print(f"Total message lines: {total_messages}")
print(f"System messages (filtered out): {system_messages}")
print(f"Actual messages: {actual_messages}")
print(f"\nParsed messages in timeline: 93")
print(f"Difference: {actual_messages - 93}")

# Check for long messages
print("\n" + "="*80)
print("Checking for very long messages...")

with open('Dec 25 Batch/_chat.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Split by message start pattern
messages = re.split(r'\n(?=\[\d{1,2}/\d{1,2}/\d{2,4},)', content)

long_messages = []
for msg in messages:
    if len(msg) > 500:  # Messages longer than 500 chars
        # Extract sender
        match = line_pattern.match(msg.split('\n')[0])
        if match:
            sender = match.group(3)
            length = len(msg)
            preview = msg[:100].replace('\n', ' ')
            long_messages.append((sender, length, preview))

print(f"Found {len(long_messages)} long messages (>500 chars):")
for sender, length, preview in long_messages[:5]:
    print(f"  - {sender}: {length} chars")
    print(f"    Preview: {preview}...")
