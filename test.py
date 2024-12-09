import whisper
import argparse
import os
import time

def transcribe_audio(file_path, model_name="base"): 
    """
    Transcribe an audio file using Whisper.

    Args:
        file_path (str): Path to the audio file to transcribe.
        model_name (str): Whisper model to use (e.g., "tiny", "base", "small", "medium", "large").

    Returns:
        dict: The transcription result containing keys like 'text', 'segments', etc.
    """
    # Load the Whisper model
    model = whisper.load_model(model_name)

    # Transcribe the audio file
    result = model.transcribe(file_path)
    return result

def save_segments_to_file(segments, file_path):
    """
    Save transcription segments to a file, matching the command-line tool's format.

    Args:
        segments (list): List of transcription segments.
        file_path (str): Path to save the transcription.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        for segment in segments:
            start = segment['start']
            end = segment['end']
            text = segment['text']
            f.write(f"[{start:.2f} --> {end:.2f}] {text}\n")

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI's Whisper model.")
    parser.add_argument("file", type=str, help="Path to the audio file.")
    parser.add_argument("--model", type=str, default="base", help="Whisper model to use (tiny, base, small, medium, large).")
    parser.add_argument("--output", type=str, help="Path to save the transcription.")

    args = parser.parse_args()
    print(args.file)
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

if __name__ == '__main__':
    main()