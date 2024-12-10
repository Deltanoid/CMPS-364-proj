import whisper

def transcribe_audio(file_path, model_name="turbo", device="cuda"): 
    """
    Args:
        file_path (str): Path to the audio file to transcribe.
        model_name (str): Whisper model to use ("small", "medium", "large", "turbo").
    Returns:
        dict: The transcription result containing keys like 'text', 'segments', etc.
    """
    model = whisper.load_model(model_name, device=device)
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
