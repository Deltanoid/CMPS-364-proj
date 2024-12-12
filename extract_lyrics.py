# for manipulating the all_songs_data.json and assosciated files
import json
import re # regular expressions
import os

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

def save_links(folder_path = 'original_lyrics/'): # go through current files in original_lyrics/ and extract the links to a seprate file
    try:
        # Get a list of all files in the folder
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        links = []
        for fname in files:
            file_path = os.path.join(folder_path, fname)
            with open(file_path) as f:
                first_line = f.readline().strip()
                links.append((fname, first_line))
        with open('links.txt',"w", encoding="utf-8") as f:
            for tup in links:
                f.write(tup[0] + " " + tup[1] +"\n")
        print("Extraced and saved links.")
        return
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' does not exist.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

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
    save_links()
