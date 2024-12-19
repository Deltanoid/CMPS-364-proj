from pydub import AudioSegment
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import torch
from torchvision import models, transforms
from PIL import Image

class AudioAnalysis:
    def __init__(self, mp3_path):
        self.mp3_path = mp3_path
        self.wav_path = mp3_path.replace('.mp3', '.wav')

    # Convert MP3 to WAV
    def convert_mp3_to_wav(self):
        audio = AudioSegment.from_mp3(self.mp3_path)
        audio.export(self.wav_path, format="wav")

    # Generate Mel Spectrogram to analyze it and further extract more information
    def create_mel_spectrogram(self, output_image="mel_spectrogram.png"):
        try:
            # Load the audio file
            y, sr = librosa.load(self.wav_path, sr=None)

            # Create a Mel spectrogram
            S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=128)

            # Convert to decibels
            S_dB = librosa.power_to_db(S, ref=np.max)

            # Plot and save the spectrogram
            plt.figure(figsize=(10, 4))
            librosa.display.specshow(S_dB, sr=sr, hop_length=512, x_axis="time", y_axis="mel")
            plt.colorbar(format="%+2.0f dB")
            plt.title("Mel Spectrogram")
            plt.tight_layout()
            plt.savefig(output_image)
            plt.close()

            print(f"Mel spectrogram saved to {output_image}")

        except Exception as e:
            print(f"Error generating spectrogram: {e}")


    # Apply a sentiment analysis to the generated spectrogram using Resnet18 CNN model
    def predict_sentiment_from_spectrogram(self, image_path, model_name="resnet18"):
        try:
            model = models.__dict__[model_name](pretrained=True)
            model.fc = torch.nn.Linear(model.fc.in_features, 3)  # Assuming 3 sentiment classes
            model.eval()

            # Define image transformations
            preprocess = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            # Load and preprocess the image
            image = Image.open(image_path).convert("RGB")
            input_tensor = preprocess(image).unsqueeze(0)

            # Run the model
            with torch.no_grad():
                outputs = model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                predicted_class = torch.argmax(probabilities).item()

            # Map class indices to sentiments
            sentiment_classes = ["Happy", "Sad", "Neutral"]
            sentiment = sentiment_classes[predicted_class]
            confidence = probabilities[predicted_class].item()

            return sentiment, confidence

        except Exception as e:
            print(f"Error during sentiment prediction: {e}")
            return None, None

    # This function extracts as many features as we can from the spectrogram
    def extract_audio_features(self, mel_spectrogram, sr):
        features = {}
        set_of_notes = {
            0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#',
            9: 'A', 10: 'A#', 11: 'B'
        }

        # Rhythm
        onset_env = librosa.onset.onset_strength(S=mel_spectrogram, sr=sr)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        features['tempo'] = tempo
        features['beats'] = beats

        # Texture
        spectral_contrast = librosa.feature.spectral_contrast(S=mel_spectrogram, sr=sr)
        average_spectral_contrast = spectral_contrast.mean(axis=1)
        avg_contrast = np.mean(average_spectral_contrast) / 100
        print("\n\navg contrast:",avg_contrast)
        features['average_spectral_contrast'] = avg_contrast
        # Classify the genre based on the average spectral contrast value
        # if avg_contrast < 0.3:
        #     features['type'] = "Classical / Ambient / Smooth Instrumental"
        # elif 0.3 <= avg_contrast < 0.5:
        #     features['type'] = "Jazz / Pop / Soft Rock"
        # elif 0.5 <= avg_contrast < 0.7:
        #     features['type'] = "Rock / Electronic / Hip Hop"
        # else:
        #     features['type'] = "Heavy Metal / Noisy / Percussive"

        # Noise and Percussion
        spectral_bandwidth = np.average(librosa.feature.spectral_bandwidth(S=mel_spectrogram, sr=sr))
        features['spectral_bandwidth'] = spectral_bandwidth

        # Extract the dominant note
        stft = librosa.stft(mel_spectrogram)  # Compute STFT
        chroma = librosa.feature.chroma_stft(S=np.abs(stft), sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        Dominant_note_idx = np.argmax(chroma_mean) % 12  # Ensure valid note index
        Dominant_note = set_of_notes[Dominant_note_idx]
        features['Dominant_Note'] = Dominant_note

        return features

    def analyze(self):
        # Load the audio file
        y, sr = librosa.load(self.wav_path)

        # Create Mel spectrogram
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)

        # Extract audio features
        features = self.extract_audio_features(mel_spectrogram, sr)

        return features


if __name__ == "__main__":
    # Example usage
    song_path = "songs/Psychostick - I Can Only Count to FOUR.mp3"
    audio_analysis = AudioAnalysis(song_path)

    # Convert MP3 to WAV
    audio_analysis.convert_mp3_to_wav()
    print("Conversion from mp3 to wav complete")

    # Create and save Mel Spectrogram
    audio_analysis.create_mel_spectrogram()

    # Analyze the audio features
    audio_analysis.analyze()
