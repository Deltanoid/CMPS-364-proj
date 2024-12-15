import argparse
import os
import time
import numpy as np
import warnings
from openai import OpenAI
import whisper_script
import sentiments_script
import prompt_script
import art_script
import instrumentals_script

def main():


    # argument handling
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI's Whisper model.")
    parser.add_argument("file", type=str, help="Path to the audio file.")
    parser.add_argument("--model", type=str, default="turbo", help="Whisper model to use (small, medium, large, turbo).")
    # parser.add_argument("--output", type=str, help="Path to save the transcription.")
    parser.add_argument("--depth", type=int, default=4, help="Layers to stop at (1: whisper, 2: semantics, 3: prompt, 4: image)")
    parser.add_argument("-v","--verbose", action='store_true', help="print the transcribed lyrics")
    parser.add_argument("-w","--warnings", action='store_true', help="unsuppress warnings")
    parser.add_argument("--mode", type=str, default="lyrical", help="lyrical, instrumental, or hybrid")
    args = parser.parse_args()

    if not args.warnings:
        print("\n\nNote: Certain warnings are suppressed!")
        warnings.filterwarnings("ignore")

    print(f"\n\nfile: {args.file}")

    # Check if the file exists
    if not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}")
        return
    song_name = (args.file).split('.mp3', 1)[0].split('/')[-1]


    ###################################
    #          Transcription          #
    ###################################
    
    # lyrics
    if (args.mode == 'lyrical' or args.mode == 'hybrid'):
        start = time.time()
        print(f"Loading model: {args.model}")
        transcription_results = whisper_script.transcribe_audio(args.file, model_name=args.model)
        end = time.time()
        detected_language = transcription_results.get('language')

        # Print and save the transcription
        if "segments" in transcription_results:
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

    # background music
    if (args.mode == 'instrumental' or args.mode == 'hybrid'):
        audio_analizer = instrumentals_script.AudioAnalysis(args.file)

        start = time.time()
        audio_analizer.convert_mp3_to_wav()
        end = time.time()
        print(f"Conversion from mp3 to wav completed in {end - start} seconds.")

        start = time.time()
        audio_analizer.create_mel_spectrogram(f'spectograms/{song_name}.png')
        end = time.time()
        print(f"mel spectogram created in {end - start} seconds")

        start = time.time()
        audi_features = audio_analizer.analyze()
        end = time.time()
        print("\n=== Transcription Complete ===")
        print(f"song features extarcted in {end - start} seconds")
        if args.verbose:
            for feature_name, feature_values in audi_features.items():
                print(f"{feature_name}: {feature_values.shape if isinstance(feature_values, np.ndarray) else feature_values}")

    if (not (args.mode == 'lyrical' or args.mode == 'instrumental' or args.mode == 'hybrid')):
        print(f"\"{args.mode}\" is not a valid mode")
        return
    
    ###################################
    #        Semantic Analysis        #
    ###################################
    if (args.depth > 1 and (args.mode == 'lyrical' or args.mode == 'hybrid')):
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
            if(args.mode == "lyrical"):
                prompt = prompt_script.generate_art_prompt(client,
                                                           text=semantics_results['original_lyrics'],
                                                           analysis_results=semantics_results['detailed_analysis'],
                                                           sentiment=semantics_results['hugging_sentiment'],
                                                           model="gpt-3.5-turbo")
            elif(args.mode == "instrumental"):
                prompt = prompt_script.generate_art_prompt(client,
                                                           instrumental_analysis=audi_features,
                                                           model="gpt-3.5-turbo")
            else: # hybrid
                prompt = prompt_script.generate_art_prompt(client, 
                                                           text=semantics_results['original_lyrics'], 
                                                           analysis_results=semantics_results['detailed_analysis'], 
                                                           sentiment=semantics_results['hugging_sentiment'], 
                                                           instrumental_analysis=audi_features, 
                                                           model="gpt-3.5-turbo")
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
            img_path = art_script.generate_image_with_dalle(prompt, client, song_name)
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