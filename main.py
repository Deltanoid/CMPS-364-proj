import argparse
import os
import time
from whisper_script import *

def main():
    # argument handling
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI's Whisper model.")
    parser.add_argument("file", type=str, help="Path to the audio file.")
    parser.add_argument("--model", type=str, default="turbo", help="Whisper model to use (small, medium, large, turbo).")
    parser.add_argument("--output", type=str, help="Path to save the transcription.")
    parser.add_argument("--depth", type=int, default=4, help="Layers to stop at (1: whisper, 2: semantics, 3: prompt, 4: image)")

    args = parser.parse_args()
    print(f"file: {args.file}")

    # Check if the file exists
    if not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}")
        return

    # Transcribe the audio file
    start = time.time()
    print(f"Loading model: {args.model}")
    result = transcribe_audio(args.file, model_name=args.model)
    end = time.time()
    print(f'\ntime taken: {end-start}\n')
    # Print and optionally save the transcription
    if "segments" in result:
        if args.output:
            save_segments_to_file(result["segments"], args.output)
            print(f"Transcription saved to: {args.output}")
        else:
            for segment in result["segments"]:
                start = segment['start']
                end = segment['end']
                text = segment['text']
                print(f"[{start:.2f} --> {end:.2f}] {text}")
    else:
        print("No transcription segments found.")
    
    
    # semantic analysis
    if (args.depth > 1):
        return
    # prompt generation
    if (args.depth > 2):
        return
    # image generation
    if (args.depth > 3):
        return

if __name__ == '__main__':
    main()
