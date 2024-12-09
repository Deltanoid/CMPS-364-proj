import whisper

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