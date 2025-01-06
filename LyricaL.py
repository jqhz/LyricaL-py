import re
import time
import syncedlyrics
import tkinter as tk
from tkinter import Label
import spotipy
import os
from dotenv import load_dotenv
import asyncio
import threading

# Code to load environment variables and create SpotifyOAuth Object to make GET requests
load_dotenv(dotenv_path=".env")
spotify_client_id=os.getenv("SPOTIPY_CLIENT_ID")
spotify_client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
spotify_redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI")

scope = 'user-read-currently-playing'
oauth_object = spotipy.SpotifyOAuth(client_id=spotify_client_id,
                                client_secret=spotify_client_secret,
                                redirect_uri=spotify_redirect_uri,
                                scope=scope)
token_dict=oauth_object.get_cached_token()
token=token_dict['access_token']
spotify_object = spotipy.Spotify(auth=token)

# Create tkinter window and label to display the lyrics
root = tk.Tk()
root.geometry("800x200+100+100")  # Set initial size and position
root.overrideredirect(True)  # Remove window decorations (title bar, etc.)
root.attributes("-transparentcolor", "pink")  # Make 'pink' fully transparent
root.attributes("-topmost", True)  # Keep the window always on top
root.title("LyricaL")
drag_start_x = 0
drag_start_y = 0

def on_drag_start(event):
    drag_start_x = event.x
    drag_start_y = event.y

def on_dragging(event):
    root_x = root.winfo_x() + (event.x - drag_start_x)
    root_y = root.winfo_y() + (event.y - drag_start_y)
    root.geometry(f"+{root_x}+{root_y}")

root.bind("<ButtonPress-1>", on_drag_start)
root.bind("<B1-Motion>", on_dragging)

lyrics_label = Label(root, text="", font=("Helvetica", 20), bg="black", fg="white", wraplength=780, justify="center")
lyrics_label.pack(expand=True)

async def update_display():
    while True:
        global status,line,track_id,artist,song_title,current_progress
        fetch_lyrics()
        #song_changed_event.wait()
        #print("EEEEEEEEEEEEEE")
        if(track_id is None):
            continue
        else:
            update_overlay_text()
        #line=track_id
        #print(line)
        #line_set_event.set()
def fetch_lyrics():
    global status,line,track_id,artist,song_title,current_progress,lines
    song_changed_event.wait()
    song_changed_event.clear()
    if status == 'track':
        print(artist + ": " + song_title)
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
                
                aline = " ".join(words)

                # Convert main timestamp to seconds
                minutes, seconds = map(float, main_timestamp.split(":"))
                timestamp_in_seconds = minutes * 60 + seconds

                lines.append((timestamp_in_seconds, aline))
    elif status == 'ad':
        print("ad")
    print( "i fetched lyrics")
    #lyrics_fetched_event.set()
# Fetch synced lyrics (based on syncedlyrics documentation)
#current_track_id=None
def update_overlay_text():
    global line,track_id,artist,song_title,current_progress,lines
    def find_nearest_time(current_progress, lines):
        """
        Find the nearest lyric line based on the current progress.
        :param current_progress: Current playback time in seconds.
        :param lines: List of tuples where each tuple contains (timestamp_in_seconds, lyric_line).
        :return: The lyric line corresponding to the nearest timestamp.
        """
        # Filter lines to include only those with timestamps <= current progress
        filtered_lines = list(filter(lambda x: x[0] <= current_progress, lines))
        
        if not filtered_lines:
            # If no lines have timestamps <= current progress, return the first line
            return lines[0][1]
        else:
            # Find the line with the maximum timestamp <= current progress
            nearest_line = max(filtered_lines, key=lambda x: x[0])
            return nearest_line[1]

    # Check if the lines are available or if any error occurred
    if not lines or not isinstance(lines, list):
        return

    # Find the nearest lyric line to the current playback time
    line = find_nearest_time(current_progress, lines)
    print(line)
    # Trigger an event to update the overlay
    line_set_event.set()
async def monitor_song():
    current_track_id = None
    while True:
        global status,line,track_id,artist,song_title,current_progress
        try:
            current = spotify_object.current_user_playing_track()

            if current and current['item']:
                status = current['currently_playing_type']
                track_id = current['item']['id']
                artist = current['item']['album']['artists'][0]['name']
                song_title = current['item']['name']
                progress_ms = current["progress_ms"]
                progress_sec = progress_ms // 1000
                progress_min = progress_sec // 60
                progress_sec %= 60
                current_progress = progress_min * 60 + progress_sec

                if track_id != current_track_id:
                    current_track_id=track_id
                    song_changed_event.set()
                    print(5)
            await asyncio.sleep(.1)
        except Exception as e:
            print("ERROR IN MONITOR_SONG()")
            await asyncio.sleep(5)
async def root_loop():
    while True:
        line_set_event.wait()
        #lyrics_fetched_event.wait()
        print("test")
        lyrics_label.config(text=line)
        root.update()
        line_set_event.clear()
        
        #lyrics_fetched_event.clear() 
        
# Thread for getting user's current song playing
def run_event_loop():
    asyncio.run(monitor_song())

def run_second_loop():
    asyncio.run(update_display())
def run_third_loop():
    asyncio.run(root_loop())
# Thread for getting lyrics on display
song_changed_event = threading.Event()
lyrics_fetched_event = threading.Event()
line_set_event=threading.Event()
threading.Thread(target=run_event_loop).start()
threading.Thread(target=run_second_loop).start()
threading.Thread(target=run_third_loop).start()
track_id = ""
artist = ""
song_title = ""
current_progress = 0
line = ""
status = ""

lines = []
actual_line = ""
time_str=""
parsed_lyrics={}
timestampsInSeconds=[]
root.mainloop()

