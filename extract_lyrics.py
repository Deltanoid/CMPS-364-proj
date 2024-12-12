# for manipulating the all_songs_data.json and assosciated files
import json
import re # regular expressions

def save_song_details(json_data):
    artist = json_data["Artist"]
    album = json_data["Album"]
    lyrics = json_data["Lyrics"]
    media = json_data["Media"]
    
    if not lyrics:
        print("Lyrics not found!")
        return
    
    normalized_lyrics = re.sub(r"\[.*?\]", "", lyrics).strip() # remove [Verse ...], [Chorus], etc.

    # Extract YouTube URL from the Media field
    media_list = json.loads(media.replace("'", '"'))  # Replace single quotes for valid JSON
    youtube_url = next((item["url"] for item in media_list if item["provider"] == "youtube"), None)

    if not youtube_url: # dont save if no url
        print("YouTube URL not found!")
        return

    # Create the file name
    file_name = f"original_lyrics/{artist} - {album}.txt"

    # Save the URL and lyrics to the file
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(youtube_url + "\n\n")
        file.write(normalized_lyrics)

    print(f"File saved as: {file_name}")


# import os
# os.chdir('C:\\Users\\alimo\\Desktop')
def driver(fname, limit = 20):
    with open(fname) as f:
        data = json.load(f)
        counter = 0
        for song in data:
            if counter < limit:
                save_song_details(song)
                counter += 1
            else:
                break
        # test = data[6]['Artist']
        # print(test)
        
if __name__=='__main__':
    fname = 'all_songs_data.json'
    #driver(fname,100)
