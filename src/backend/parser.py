import re
import os
import unicodedata
from datetime import datetime, timedelta
from typing import List, Dict, Any

class ChatParser:
    def __init__(self, chat_file: str, images_dir: str, original_chat_file: str = None):
        self.chat_file = chat_file
        self.images_dir = images_dir
        self.original_chat_file = original_chat_file
        # Updated to handle 2 or 4 digit years: \d{2,4}
        self.timestamp_pattern = r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),' 
        self.image_pattern = r'(\d{4})-(\d{2})-(\d{2})'
        self.video_date_map = self._build_video_date_map() if original_chat_file else {}
        
    def _build_video_date_map(self) -> dict:
        """
        Scans the original WhatsApp export (_chat.txt) to find when YouTube links 
        were actually shared. Returns a map of {video_id: date_string}.
        """
        date_map = {}
        if not self.original_chat_file or not os.path.exists(self.original_chat_file):
            print(f"Warning: Original chat file not found at {self.original_chat_file}")
            return date_map
            
        try:
            with open(self.original_chat_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # Look for YouTube links
                    if "youtu" in line and "http" in line:
                        # Extract Date: [9/28/25, ...
                        # Regex for standard WhatsApp export date: [M/D/YY, ...
                        date_match = re.search(r'\[(\d{1,2}/\d{1,2}/\d{2,4}),', line)
                        if date_match:
                            date_str = date_match.group(1)
                            # Normalize year to 4 digits if needed (25 -> 2025)
                            parts = date_str.split('/')
                            if len(parts) == 3 and len(parts[2]) == 2:
                                date_str = f"{parts[0]}/{parts[1]}/20{parts[2]}"
                                
                            # Extract Video ID
                            vid_id_match = re.search(r'(?:v=|youtu\.be/)([\w\-]+)', line)
                            if vid_id_match:
                                video_id = vid_id_match.group(1)
                                date_map[video_id] = date_str
        except Exception as e:
            print(f"Error building video date map: {e}")
            
        print(f"Built video date map with {len(date_map)} entries.")
        return date_map

    def extract_video_url(self, text: str) -> str | None:
        if not text:
            return None
        
        # More robust regex for YouTube URLs
        # Matches: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID
        youtube_regex = r'https?://(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)([\w\-]+)'
        match = re.search(youtube_regex, text)
        if match:
            video_id = match.group(1)
            # Normalize to standard YouTube watch URL for better ReactPlayer compatibility
            return f"https://www.youtube.com/watch?v={video_id}"
            
        # Fallback for explicit URL: pattern
        if "URL:" in text:
            try:
                idx = text.find("URL:")
                possible_url = text[idx+4:].strip().split()[0]
                if "http" in possible_url:
                    # Try to extract video ID and normalize
                    vid_match = re.search(r'(?:v=|youtu\.be/|embed/)([\w\-]+)', possible_url)
                    if vid_match:
                        return f"https://www.youtube.com/watch?v={vid_match.group(1)}"
                    return possible_url
            except:
                pass
        
        return None

    def parse(self):
        grouped_data = {} # { "date_str": [message_objects] }
        
        try:
            with open(self.chat_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by the separator used for transcripts
            sections = content.split('================================================================')
            main_chat_lines = sections[0].splitlines()
            
            current_date_str = None
            
            # Regex to parse the chat line: [Date, Time] Sender: Message
            # Handles 2-digit (25) and 4-digit (2025) years
            line_pattern = re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}\s*[APap][Mm])\]\s*(.*?):\s*(.*)$')
            
            def parse_datetime(date_s, time_s):
                dt_str = f"{date_s} {time_s}"
                formats = [
                    "%m/%d/%y %I:%M:%S %p",   # 9/1/25 5:59:40 PM
                    "%m/%d/%Y %I:%M:%S %p",   # 9/1/2025 5:59:40 PM
                    "%d/%m/%y %I:%M:%S %p",   # DD/MM/YY fallback
                    "%d/%m/%Y %I:%M:%S %p"
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(dt_str, fmt)
                    except ValueError:
                        continue
                return datetime.now() # Fallback

            all_messages = []

            for line in main_chat_lines:
                line = line.strip()
                # Remove LTR/RTL marks
                line = line.replace('\u200e', '').replace('\u200f', '')
                
                if not line:
                    continue
                
                match = line_pattern.match(line)
                if match:
                    # New Message Start
                    date_str, time_str, sender, msg_content = match.groups()
                    dt_obj = parse_datetime(date_str, time_str)
                    
                    # Normalize date_str to MM/DD/YYYY for grouping key consistency
                    # (Uses the parsed dt_obj to reconstruct)
                    normalized_date_str = dt_obj.strftime("%m/%d/%Y")
                    
                    # Check for attachment
                    attachment_match = re.search(r'<attached:\s*(.*?)>', msg_content)
                    
                    msg_type = "text"
                    url = None
                    file_path = None
                    
                    if attachment_match:
                        filename = attachment_match.group(1).strip()
                        ext = os.path.splitext(filename)[1].lower()
                        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                            msg_type = "image"
                            file_path = f"/static/{filename}"
                        elif ext in ['.mp4', '.mov']:
                            msg_type = "video_file"
                            file_path = f"/static/{filename}"
                        
                        # Remove attachment tag from content
                        msg_content = msg_content.replace(attachment_match.group(0), "").strip()

                    else:
                        # Skip system messages
                        # Clean invisible control characters
                        msg_content = "".join(ch for ch in msg_content if unicodedata.category(ch)[0] != "C")
                        
                        # Skip system messages - Aggressive Filter
                        lower_content = msg_content.lower()
                        if "joined using a group" in lower_content or "joined using this group" in lower_content:
                             continue
                        if "security code changed" in lower_content:
                             continue
                        if "added" in lower_content:
                            # Check for patterns like "added +1..." or "added ~..." or "added you"
                            if re.search(r'added\s+[\+~]', msg_content) or "added you" in lower_content:
                                continue
                        if lower_content.strip() == "left":
                            continue

                        url = self.extract_video_url(msg_content)
                    
                    message_obj = {
                        "type": msg_type,
                        "time_obj": dt_obj, 
                        "time": time_str, 
                        "sender": sender.strip(),
                        "content": msg_content if msg_content else (file_path if file_path else ""), 
                        "is_video": True if url else False,
                        "video_url": url,
                        "image_url": file_path
                    }
                    
                    all_messages.append(message_obj)
                    current_date_str = main_chat_lines # Just reference, logic uses dt_obj

                else:
                    # Continuation of previous message
                    if all_messages:
                        # Check if this NEW line has a video URL
                        new_line_url = self.extract_video_url(line)
                        last_msg = all_messages[-1]
                        
                        # If previous message ALREADY has a video, and this line has a DIFFERENT video
                        if last_msg["is_video"] and new_line_url and new_line_url != last_msg["video_url"]:
                            # Create a new message for this video to allow multiple videos in one "block"
                            split_msg = last_msg.copy()
                            split_msg["content"] = line
                            split_msg["video_url"] = new_line_url
                            split_msg["is_video"] = True
                            split_msg["image_url"] = None
                            # Offset time slightly to preserve order
                            split_msg["time_obj"] = last_msg["time_obj"] + timedelta(milliseconds=100)
                            
                            all_messages.append(split_msg)
                        else:
                            # Standard continuation
                            all_messages[-1]["content"] += "\n" + line
                            # Re-check for URL if not found yet
                            if not all_messages[-1]["is_video"]:
                                url = self.extract_video_url(all_messages[-1]["content"])
                                if url:
                                    all_messages[-1]["is_video"] = True
                                    all_messages[-1]["video_url"] = url

            # Map video IDs to message indices
            video_map = {}
            for i, msg in enumerate(all_messages):
                if msg["is_video"] and msg["video_url"]:
                    vid_match = re.search(r'(?:v=|youtu\.be/|embed/)([\w\-]+)', msg["video_url"])
                    if vid_match:
                        video_map[vid_match.group(1)] = i

            # Process Transcripts from separate file if not found in sections
            transcript_source = sections[1:] if len(sections) > 1 else []
            
            # Process Transcripts from separate file if not found in sections
            transcript_source = sections[1:] if len(sections) > 1 else []
            
            # Check for external transcript file
            # Assuming CWD is project root
            external_transcript_file = os.path.join(os.getcwd(), "youtube_transcripts.txt")
            
            if len(transcript_source) == 0:
                print(f"Checking for transcript file at: {external_transcript_file}")
            if os.path.exists(external_transcript_file):
                print("Reading external transcripts...")
                try:
                    with open(external_transcript_file, 'r', encoding='utf-8') as tf:
                        t_lines = tf.readlines()
                    
                    current_vid_id = None
                    current_content = []
                    count_external = 0
                    
                    def flush_transcript():
                        nonlocal count_external
                        if current_vid_id and current_content:
                            clean_content = "".join(current_content).strip()
                            # Check if content is valid
                            if not clean_content: return
                            
                            if current_vid_id in video_map:
                                target_msg_idx = video_map[current_vid_id]
                                ref_msg = all_messages[target_msg_idx]
                                
                                transcript_msg = {
                                    "type": "transcript", 
                                    "time_obj": ref_msg["time_obj"] + timedelta(seconds=1), 
                                    "time": "Transcript",
                                    "sender": "Archive Bot",
                                    "content": clean_content,
                                    "is_video": False,
                                    "video_url": f"https://www.youtube.com/watch?v={current_vid_id}",
                                    "image_url": None
                                }
                                # print(f"DEBUG: Injecting transcript for {current_vid_id}")
                                all_messages.append(transcript_msg)
                                count_external += 1
                            else:
                                pass # print(f"Missed match for ID: {current_vid_id}")

                    for line in t_lines:
                        # Check for URL line which signals start of new video context
                        if "URL:" in line:
                            # Flush previous context
                            flush_transcript()
                            
                            # Start new context
                            current_content = []
                            current_vid_id = None
                            
                            vid_match = re.search(r'(?:v=|youtu\.be/|embed/)([\w\-]+)', line)
                            if vid_match:
                                current_vid_id = vid_match.group(1).strip()
                        
                        elif "[Video Transcript]" in line:
                            # Just a header, usually precedes URL. If singular, flush prev.
                            pass
                            
                        elif "=======" in line:
                            # Separator, ignore
                            pass
                            
                        else:
                            # Content line
                            if current_vid_id:
                                current_content.append(line)
                                
                    # Flush last block
                    flush_transcript()
                    
                except Exception as e:
                    print(f"Error reading transcript file: {e}")
            else:
                print("Transcript file not found!")
                
            print(f"Injected {count_external} transcripts from external file.")
                
            # Sort all messages by time
            all_messages.sort(key=lambda x: x["time_obj"])
            
            # Group by Date
            for msg in all_messages:
                d_str = msg["time_obj"].strftime("%m/%d/%Y") # Key format
                
                if d_str not in grouped_data:
                    grouped_data[d_str] = []
                
                final_msg = msg.copy()
                del final_msg["time_obj"]
                
                # Compatibility with frontend image rendering
                if final_msg["type"] == "image":
                    final_msg["content"] = final_msg["image_url"]
                
                # Transcript post-processing check
                if final_msg["type"] == "text":
                    upper_content = final_msg["content"].upper()
                    # Stricter check: Must have "END OF POST" usually used in blog reposts
                    # Explicitly exclude the Welcome message if it accidentally contains this phrase
                    if ("END OF POST" in upper_content or "END OF BLOG" in upper_content) and "WELCOME ALL TO THIS HEALTH GROUP" not in upper_content:
                        final_msg["type"] = "transcript"

                grouped_data[d_str].append(final_msg)

        except Exception as e:
            print(f"Error parse chat file: {e}")
            import traceback
            traceback.print_exc()

        # Convert to list and sort days
        timeline = [{"date": k, "messages": v} for k, v in grouped_data.items()]
        
        def parse_date_key(d_str):
            try:
                return datetime.strptime(d_str, "%m/%d/%Y")
            except:
                return datetime.max
        
        timeline.sort(key=lambda x: parse_date_key(x["date"]))
        
        return timeline

    def clean_transcript(self, text: str) -> str:
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith("URL:"):
                cleaned_lines.append(f"**Source URL:** [{line[4:].strip()}]({line[4:].strip()})\n")
                continue
            if line.startswith("[Video Transcript]"):
                cleaned_lines.append(f"### {line}\n") 
                continue
            if line.startswith("==="): continue
            
            if line and line[0].islower():
                line = line[0].upper() + line[1:]
            
            cleaned_lines.append(line + "\n\n")
        return "".join(cleaned_lines)
