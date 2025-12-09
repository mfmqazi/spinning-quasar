import json
import os
import sys

# Add src to path
sys.path.append(os.getcwd())

from src.backend.parser import ChatParser

BASE_DIR = os.getcwd()
CHAT_FILE = os.path.join(BASE_DIR, "whatsapp_export", "extracted", "_chat.txt")
ORIGINAL_CHAT_FILE = os.path.join(BASE_DIR, "whatsapp_export", "extracted", "_chat.txt")
IMAGES_DIR = os.path.join(BASE_DIR, "whatsapp_export", "extracted")
OUTPUT_FILE = os.path.join(BASE_DIR, "src", "frontend", "public", "timeline.json")

print(f"Parsing chat from {CHAT_FILE}...")
parser = ChatParser(CHAT_FILE, IMAGES_DIR, ORIGINAL_CHAT_FILE)
timeline = parser.parse()

print(f"Saving {len(timeline)} days to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(timeline, f, ensure_ascii=False, indent=2)

print("Done!")
