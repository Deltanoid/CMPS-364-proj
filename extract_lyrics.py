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

# Example JSON data (replace this with your actual JSON data)
data = {
    "Album": "Battle of New Orleans",
    "Album URL": "https://genius.com/albums/Johnny-horton/Battle-of-new-orleans",
    "Artist": "Johnny Horton",
    "Featured Artists": "[]",
    "Lyrics": "[Verse 1] In 1814 we took a little trip Along with Colonel Jackson down the mighty Mississip We took a little bacon and we took a little beans And we caught the bloody British in a town near New Orleans [Chorus] We fired our guns and the British kept a-comin' There wasn't nigh as many as there was a while ago We fired once more and they begin to runnin' On down the Mississippi to the Gulf of Mexico [Verse 2] We looked down a river (Hut-two) And we see'd the British come (Three-four) And there must have been a hundred of'em (Hut-two) Beatin' on the drums (Three-four) They stepped so high (Hut-two) And they made their bugles ring (Three-four) We stood beside our cotton bales (Hut-two) And didn't say a thing (Two-three-four) [Chorus] We fired our guns and the British kept a-comin' There wasn't nigh as many as there was a while ago We fired once more and they begin to runnin' On down the Mississippi to the Gulf of Mexico [Verse 3] Old Hickory said we could take 'em by surprise (One-hut, two-three-four) If we didn't fire our muskets (One-hut, two-three-four) 'Till we looked 'em in the eye (One-hut, two-three-four) We held our fire (Hut, two-three-four) 'Till we see their faces well Then we opened up our squirrel guns And really gave 'em - well we [Chorus] Fired our guns and the British kept a-comin' There wasn't nigh as many as there was a while ago We fired once more and they begin to runnin' On down the Mississippi to the Gulf of Mexico [Verse 4] Yeah, they ran through the briars (One-hup-two) And they ran through the brambles (Hup-two-three-four) And they ran through the bushes (Hup-two) Where the rabbit couldn't go (Hup-two-three-four) They ran so fast (Hup-two) That the hounds couldn't catch 'em (One-two-three-four) On down the Mississippi to the Gulf of Mexico (One-two, hup-two-three-four) [Verse 5] We fired our cannon 'til the barrel melted down So we grabbed an alligator and we fired another round We filled his head with cannon balls, and powdered his behind And when we touched the powder off the gator lost his mind [Chorus] We fired our guns and the British kept a-comin' There wasn't nigh as many as there was a while ago We fired once more and they begin to runnin' On down the Mississippi to the Gulf of Mexico [Verse 4] Yeah, they ran through the briars (Hup-one-two) And they ran through the brambles (One-two-three-four) And they ran through the bushes (Hup-two) Where the rabbit couldn't go (Hup-two-three-four) They ran so fast (Hup-two) That the hounds couldn't catch 'em (One-two-three-four) On down the Mississippi to the Gulf of Mexico",
    "Media": "[{'native_uri': 'spotify:track:0dwpdcQkeZqpuoAPYD49N3', 'provider': 'spotify', 'type': 'audio', 'url': 'https://open.spotify.com/track/0dwpdcQkeZqpuoAPYD49N3'}, {'provider': 'youtube', 'start': 0, 'type': 'video', 'url': 'http://www.youtube.com/watch?v=VL7XS_8qgXM'}]",
    "Rank": 1,
    "Release Date": "1959-04-01",
    "Song Title": "The Battle Of New Orleans",
    "Song URL": "https://genius.com/Johnny-horton-the-battle-of-new-orleans-lyrics",
    "Writers": "[{'api_path': '/artists/561913', 'header_image_url': 'https://images.genius.com/641ca05661977b0309ebffc9507f2baf.202x202x1.jpg', 'id': 561913, 'image_url': 'https://images.genius.com/641ca05661977b0309ebffc9507f2baf.202x202x1.jpg', 'is_meme_verified': False, 'is_verified': False, 'name': 'Jimmy Driftwood', 'url': 'https://genius.com/artists/Jimmy-driftwood'}]",
    "Year": 1959
}

import os
os.chdir('C:\\Users\\alimo\\Desktop')
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
    driver('all_songs_data.json',100)