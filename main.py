import argparse
import os
import time
import warnings
from openai import OpenAI
import whisper_script
import sentiments_script
import prompt_script
import art_script

def main():


    # argument handling
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI's Whisper model.")
    parser.add_argument("file", type=str, help="Path to the audio file.")
    parser.add_argument("--model", type=str, default="turbo", help="Whisper model to use (small, medium, large, turbo).")
    # parser.add_argument("--output", type=str, help="Path to save the transcription.")
    parser.add_argument("--depth", type=int, default=4, help="Layers to stop at (1: whisper, 2: semantics, 3: prompt, 4: image)")
    parser.add_argument("-v","--verbose", action='store_true', help="print the transcribed lyrics")
    parser.add_argument("-w","--warnings", action='store_true', help="unsuppress warnings")
    args = parser.parse_args()

    if not args.warnings:
        print("\n\nNote: Certain warnings are suppressed!")
        warnings.filterwarnings("ignore")

    print(f"\n\nfile: {args.file}")

    # Check if the file exists
    if not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}")
        return

    ###################################
    #          Transcription          #
    ###################################
    start = time.time()
    print(f"Loading model: {args.model}")
    transcription_results = whisper_script.transcribe_audio(args.file, model_name=args.model)
    end = time.time()
    detected_language = transcription_results.get('language')

    # Print and save the transcription
    if "segments" in transcription_results:
        song_name = (args.file).split('.', 1)[0].split('/')[-1]
        output_transcription = f'lyric_results/{song_name}_({args.model}).txt'
        whisper_script.save_segments_to_file(transcription_results["segments"], output_transcription)
        print("\n=== Transcription Complete ===")
        print(f'\ntime taken: {end-start}\n')
        print(f"Transcription saved to: {'lyric_results/'+output_transcription}")
        if args.verbose:
            print(f'Detected language: {detected_language}')
            for segment in transcription_results["segments"]:
                start = segment['start']
                end = segment['end']
                text = segment['text']
                print(f"[{start:.2f} --> {end:.2f}] {text}")
    else:
        print("No transcription segments found.")
    
    ###################################
    #        Semantic Analysis        #
    ###################################
    if (args.depth > 1):
        # api_key = os.getenv('OPENAI_API_KEY') # Get API key from environment variable for security
        # if not api_key:
        #     print(f"Please set the OPENAI_API_KEY environment variable")
        #     return
        api_key = get_api_key()
        client = OpenAI(api_key=api_key)

        # Initialize generator
        analyzer = sentiments_script.LyricAnalyzer(client, detected_language)
            # Analyze lyrics
        try:
            start = time.time()
            semantics_results = analyzer.analyze_lyrics(output_transcription)
            end = time.time()
            
            # Print results summary
            print("\n=== Analysis Complete ===")
            print(f"Time taken: {end-start}")
            print(f"Sentiment: {semantics_results['hugging_sentiment']}") 
            print(f"\nFull analysis results saved to: {analyzer.output_dir}")
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Check the generated JSON file for details.")
    
    ###################################
    #        Prompt Generation        #
    ###################################
    if (args.depth > 2): # currently does not actually use sentiment, needs updating
        try:
            start = time.time()
            prompt = prompt_script.generate_art_prompt(client, semantics_results['original_lyrics'], semantics_results['detailed_analysis'], "gpt-3.5-turbo")
            end = time.time()
            print("\n=== Prompt Generation Complete ===")
            print(f"Time taken: {end-start}")
            if args.verbose:
                print("--------------------")
                print(prompt)
                print("--------------------")
        except Exception as e:
            print(f"\nError: {str(e)}")
    
    ###################################
    #         Image Generation        #
    ###################################
    if (args.depth > 3):
        try:
            start = time.time()
            img_path = art_script.generate_image_with_dalle(prompt, client, output_transcription[:-4])
            end = time.time()
            print("\n=== Image Generation Complete ===")
            print(f"Time taken: {end-start}")
            print(f"Image path: {img_path}")
        except Exception as e:
            print(f"\nError: {str(e)}")

def get_api_key(file_path="api_key.txt"):
    try:
        with open(file_path, "r") as file:
            first_line = file.readline().strip()  # Read and strip any leading/trailing whitespace
            return first_line
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
   
if __name__ == '__main__':
    main()