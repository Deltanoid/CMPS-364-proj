import argparse
import os
import time
import whisper_script
import sentiments_script

def main():
    # argument handling
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI's Whisper model.")
    parser.add_argument("file", type=str, help="Path to the audio file.")
    parser.add_argument("--model", type=str, default="turbo", help="Whisper model to use (small, medium, large, turbo).")
    # parser.add_argument("--output", type=str, help="Path to save the transcription.")
    parser.add_argument("--depth", type=int, default=4, help="Layers to stop at (1: whisper, 2: semantics, 3: prompt, 4: image)")
    parser.add_argument("-v","--verbose", action='store_true', help="print the transcribed lyrics")

    args = parser.parse_args()
    print(f"file: {args.file}")

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
    print(f'\ntime taken: {end-start}\n')
    detected_language = transcription_results.get('language')

    # Print and save the transcription
    if "segments" in transcription_results:
        output_transcription = (args.file).split('.', 1)[0] + '.txt' # extract file name
        whisper_script.save_segments_to_file(transcription_results["segments"], output_transcription)
        print(f"Transcription saved to: {output_transcription}")
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
        api_key = os.getenv('OPENAI_API_KEY') # Get API key from environment variable for security
        if not api_key:
            print(f"Please set the OPENAI_API_KEY environment variable")
            return
        
        # Initialize generator
        analyzer = sentiments_script.LyricAnalyzer(api_key, detected_language)
            # Analyze lyrics
        try:
            start = time.time()
            semantics_results = analyzer.analyze_lyrics()
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
    if (args.depth > 2):
        return
    
    ###################################
    #         Image Generation        #
    ###################################
    if (args.depth > 3):
        return

if __name__ == '__main__':
    main()