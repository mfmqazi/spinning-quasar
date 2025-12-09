import re
import os

def test_parsing():
    file_path = "whatsapp_export/extracted/_chat.txt"
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    line_pattern = re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}\s*[APap][Mm])\]\s*(.*?):\s*(.*)$')
    
    attachment_count = 0
    
    for line in lines:
        clean_line = line.strip().replace('\u200e', '').replace('\u200f', '')
        match = line_pattern.match(clean_line)
        if match:
            date_str, time_str, sender, msg_content = match.groups()
            if "<attached" in msg_content:
                 print(f"Found attached in content: {msg_content}")
                 attachment_match = re.search(r'<attached:\s*(.*?)>', msg_content)
                 if attachment_match:
                     print(f"  -> Extracted: {attachment_match.group(1)}")
                     attachment_count += 1
                 else:
                     print("  -> Regex extraction FAILED")
    
    print(f"Total attachments found: {attachment_count}")

if __name__ == "__main__":
    test_parsing()
