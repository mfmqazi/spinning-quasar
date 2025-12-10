import json
import os
import sys

# Add src to path
sys.path.append(os.getcwd())

from src.backend.parser import ChatParser

BASE_DIR = os.getcwd()
# Updated to use the latest December 2025 export (through Dec 9, 2025)
DEC_CHAT_FILE = os.path.join(BASE_DIR, "Dec 25 Batch - 12-Dec-25", "_chat.txt")
DEC_IMAGES_DIR = os.path.join(BASE_DIR, "Dec 25 Batch - 12-Dec-25")
OUTPUT_FILE = os.path.join(BASE_DIR, "src", "frontend", "public", "timeline_dec2025.json")

print(f"Parsing December 2025 chat from {DEC_CHAT_FILE}...")
parser = ChatParser(DEC_CHAT_FILE, DEC_IMAGES_DIR, DEC_CHAT_FILE)
timeline = parser.parse()

print(f"Saving {len(timeline)} days to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(timeline, f, ensure_ascii=False, indent=2)

print("Done!")
print(f"December 2025 timeline has {sum(len(day['messages']) for day in timeline)} messages")
