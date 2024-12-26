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

'''def getTrackInfo():
    current_track = spotify_object.current_user_playing_track()
    if current_track is None or (current_track['item'] is None):
        return None
    artist = current_track['item']['artists'][0]['name']
    track_name = current_track['item']['name']
    is_playing = current_track['is_playing']
    progress_ms = current_track['progress_ms']
    
    # Convert progress_ms to minutes and seconds
    progress_sec = progress_ms // 1000
    progress_min = progress_sec // 60
    progress_sec %= 60
    return {
        'artist': artist,
        'trackName': track_name,
        'progressMin': progress_min,
        'progressSec': progress_sec,
        'isPlaying': is_playing
    }
async def update_track_info():
    while True:
        global trackName,artist,currentProgress,isPlaying
        trackName,artist,currentProgress,isPlaying = getTrackInfo()
        time.sleep(.1)'''

async def fetch_lyrics(song_title,artist,track_id):
    current = spotify_object.current_user_playing_track()
    status = current['currently_playing_type']
    #track_id=current['item']['id']
    print("status: "+status)
    try:
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
                    current = spotify_object.current_user_playing_track()
                    print("sys id:"+ current['item']['id'])
                    print("track id: "+ track_id)
                    if (current['item']['id']) != track_id:
                        return
                    while time.time()-start_time < target_time:
                        time.sleep(0.01)  # Small delay to synchronize
                    lyrics_label.config(text=line)
                    root.update()               
        elif status == 'ad':
            print("ad")
    except Exception as e:
        print("Error")
    
# Fetch synced lyrics (based on syncedlyrics documentation)
#current_track_id=None

async def monitor_song():
    current_track_id = None
    while True:
        try:
            current = spotify_object.current_user_playing_track()

            if current and current['item']:
                
                track_id = current['item']['id']
                artist = current['item']['album']['artists'][0]['name']
                song_title = current['item']['name']
                if track_id != current_track_id:
                    current_track_id=track_id
                    print("track id: "+track_id)
                    print("artist: "+artist)
                    print("song title: "+song_title)
                    print("current_track_id: "+current_track_id)
                    print("\n")
                    await fetch_lyrics(song_title,artist,track_id)
                    print(5)
            await asyncio.sleep(5)
        except Exception as e:
            print("aaaaaaaaaaaaaaaaaa")
            await asyncio.sleep(5)

def run_event_loop():
    asyncio.run(monitor_song())

threading.Thread(target=run_event_loop,daemon=True).start()

root.mainloop()