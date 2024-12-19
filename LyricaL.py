import re
import time
import syncedlyrics

# Initialize the lyrics client
#client = SomeClientClass()  # Replace with the correct initialization method.

# Example: Fetch lyrics for "Ain't It Fun" by Paramore
song_title = "Ain't It Fun"
artist = "Paramore"

# Fetch synced lyrics (adjust the method based on syncedlyrics documentation)
results = syncedlyrics.search(song_title +" " +artist,enhanced=True)
print(results)
'''if not results:
    print("No lyrics found!")
else:
    # Get lyrics (assuming the first result is correct)
    lyrics_data = results

    # Regular expression to extract <timestamp> word pairs
    pattern = r"<(\d{2}:\d{2}\.\d{2})>\s*([\w',?!.]+)"
    matches = re.findall(pattern, lyrics_data)

    # Convert timestamps to seconds
    def time_to_seconds(timestamp):
        minutes, seconds = map(float, timestamp.split(":"))
        return minutes * 60 + seconds

    # Sort the lyrics by timestamp
    sorted_lyrics = sorted(matches, key=lambda x: time_to_seconds(x[0]))

    # Print each word at its respective timestamp
    start_time = time.time()
    for timestamp, word in sorted_lyrics:
        target_time = time_to_seconds(timestamp)
        while time.time() - start_time < target_time:
            time.sleep(0.01)  # Small delay to sync output
        print(word)'''