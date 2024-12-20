import re
import time
import syncedlyrics
import tkinter as tk
from tkinter import Label

song_title = "Primadonna"
artist = "MARINA"

root = tk.Tk()
root.geometry("800x200+100+100")  # Set initial size and position
root.overrideredirect(True)  # Remove window decorations (title bar, etc.)
root.attributes("-transparentcolor", "pink")  # Make 'pink' fully transparent
root.attributes("-topmost", True)  # Keep the window always on top

lyrics_label = Label(root, text="", font=("Helvetica", 20), bg="black", fg="white", wraplength=780, justify="center")
lyrics_label.pack(expand=True)
# Fetch synced lyrics (based on syncedlyrics documentation)
results = syncedlyrics.search(song_title +" " +artist,enhanced=True)

if not results:
    print("No lyrics found!")
else:
    lyrics_data = results
    # Regular expression to match line header timestamp
    line_pattern = r"\[(\d{2}:\d{2}\.\d{2})].*?(<\d{2}:\d{2}\.\d{2}>\s*[\w',?!.]+.*)"
    matches = re.findall(line_pattern, lyrics_data)

    
    lines = []
    # For each timestamped word
    for match in matches:
        main_timestamp, raw_line = match

        # Regular expression to match <> tags but only include words after
        word_pattern = r"<\d{2}:\d{2}\.\d{2}>\s*([\w',?!.]+)"
        words = re.findall(word_pattern, raw_line)
        
        line = " ".join(words)

        # Convert main timestamp to seconds
        minutes, seconds = map(float, main_timestamp.split(":"))
        timestamp_in_seconds = minutes * 60 + seconds

        lines.append((timestamp_in_seconds, line))

    # Sort lines by their timestamps
    #lines.sort(key=lambda x: x[0]) redundant

    # Print each line at its respective timestamp
    start_time = time.time()
    for target_time, line in lines:
        while time.time()-start_time < target_time:
            time.sleep(0.01)  # Small delay to synchronize
        lyrics_label.config(text=line)
        root.update()
        