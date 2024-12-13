# for getting the word & character error rates of generated lyrics compared to provided ones
from jiwer import wer, cer
import os
import re

def calculate_wer(original_text, generated_text):
    # Calculate Word Error Rate (WER) and Character Error Rate (CER) between two texts.

    word_error_rate = wer(original_text, generated_text)
    char_error_rate = cer(original_text, generated_text)
    return (word_error_rate, char_error_rate)

def load_original(folder_path='original_lyrics'): # return dict of dict of lyrics
    try:
        # Get a list of all files in the folder
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        songs = {}
        for fname in files:
            file_path = os.path.join(folder_path, fname)
            with open(file_path) as f:
                lines = f.readlines()
                cleaned_lines = []
                lines = lines[2:] # skip link and empty line
                for line in lines:
                    line = re.sub(r"[.,!?]", "", line) # Remove punctuation
                    cleaned_lines.append(line.strip())
                lyrics = {'original': " ".join(cleaned_lines)}
                songs[fname.split('.txt')[0]] = lyrics
        print("Extraced lyrics.")
        return songs
    except FileNotFoundError:
        print(f"load_original Error: The folder '{folder_path}' does not exist.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}
    
def load_lyrics(folder_path='original_lyrics', models = ['small','turbo','large']):
    songs = load_original(folder_path)
    scores = []
    for fname, lyrics in songs.items():
        model_scores = {}
        try:
            for model in models:
                with open(os.path.join('lyric_results', f'{fname}_({model}).txt')) as f:
                    lines = f.readlines()
                cleaned_lines = []
                for line in lines:
                    
                    line = re.sub(r"\[.*?\]", "", line) # Remove timestamps
                    line = re.sub(r"[.,!?]", "", line) # Remove punctuation
                    cleaned_lines.append(line.strip()) # strip leading/trailing whitespace

                lyrics[model] = " ".join(cleaned_lines)
            for model in models:
                word_e, char_e = calculate_wer(lyrics['original'],lyrics[model])
                model_scores[model] = (word_e, char_e)
            scores.append((fname,model_scores))
        except FileNotFoundError:
            print(f"load_lyrics Error: The location '{os.path.join('lyric_results', fname)}' does not exist.")
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return

    return scores

if __name__ == "__main__":
    # original = "this is a sample text to evaluate word error rate of this text"
    # generated = "this is sample text evaluate the error rate of this text"

    # word_error_rate, char_error_rate = calculate_wer(original, generated)

    # print("=== Error Rates ===")
    # print(f"Word Error Rate (WER): {word_error_rate:.2%}")
    # print(f"Character Error Rate (CER): {char_error_rate:.2%}")

    scores = load_lyrics()
    sorted_scores = scores.sort(key = lambda tup: tup[0]) # sort by name
    print("=== Error Rates ===")
    for song, model_scores in scores:
        for model, score in model_scores.items():
            print(f'{song} ({model}) ---> WER: {score[0]:.2f}, CER: {score[1]:.2f}')
        print('\n')