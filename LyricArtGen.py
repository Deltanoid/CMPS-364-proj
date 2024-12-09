import os
from openai import OpenAI
from transformers import pipeline
import json
from datetime import datetime
from pathlib import Path
import requests

class LyricArtGenerator:
    def __init__(self, openai_api_key):
        """Initialize with OpenAI API key and Arabic sentiment analyzer."""
        self.client = OpenAI(api_key=openai_api_key)
        #distilbert-base-uncased-finetuned-sst-2-english
        self.sentiment_pipeline = pipeline("text-classification", 
                                        model="PRAli22/AraBert-Arabic-Sentiment-Analysis")
        self.output_dir = Path("generated_artwork")
        self.output_dir.mkdir(exist_ok=True)

    def read_lyrics(self, file_path):
        """Read lyrics file with proper encoding."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp1256') as file:
                return file.read()

    def get_arabic_sentiment(self, text):
        """Get sentiment using Arabic-specific model."""
        results = self.sentiment_pipeline(text)
        return results[0] if results else None

    def analyze_with_gpt(self, text):
        """Analyze lyrics using GPT for deeper understanding."""
        prompt = f"""Analyze the following lyrics deeply and provide a structured analysis:

Lyrics:
{text}

Please provide:
1. Major themes and motifs
2. Emotional undertones
3. Notable imagery and metaphors
4. Cultural or historical references
5. Key symbols and their significance
6. Overall tone and atmosphere

Format the response as a JSON object with these categories as keys.
Make the analysis rich and specific, but keep each point concise."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a literary expert specialized in analyzing lyrics and poetry. Provide deep, insightful analysis while maintaining objectivity."},
                    {"role": "user", "content": prompt}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error in GPT analysis: {str(e)}")


############################################################################


    def generate_art_prompt(self, text, analysis_results):
        """Generate an art prompt based on the analysis."""
        prompt = f"""Based on this lyrical analysis, create an artistic prompt for DALL-E.

Analysis:
{json.dumps(analysis_results, indent=2)}

Original Lyrics:
{text}

Create a detailed, vivid prompt that:
1. Captures the essence and emotion of the lyrics
2. Incorporates major themes and imagery
3. Suggests specific visual elements, colors, and composition
4. Maintains artistic cohesion
5. Includes style suggestions (e.g., realistic, surreal, abstract)

Important: Create a prompt that's optimized for DALL-E image generation. 
Keep it clear, specific, and under 400 characters.
Focus on visual elements and artistic style.
Avoid abstract concepts that can't be visualized.

Format the response as a JSON object with these keys:
- main_prompt: the primary prompt text (optimized for DALL-E)
- style_suggestions: list of artistic style recommendations
- color_palette: suggested colors that match the emotional tone
- key_elements: list of important visual elements to include"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating artistic prompts that capture the essence of literary works."},
                    {"role": "user", "content": prompt}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error in prompt generation: {str(e)}")

    def generate_image_with_dalle(self, art_prompt):
        """Generate image using DALL-E based on the art prompt."""
        try:
            # Extract the main prompt and style from the art prompt
            main_prompt = art_prompt['main_prompt']
            style = ", ".join(art_prompt['style_suggestions'][:2])  # Use top 2 style suggestions
            final_prompt = f"{main_prompt} Style: {style}"

            # Generate image with DALL-E
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=final_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            # Get image URL
            image_url = response.data[0].url

            # Download and save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = self.output_dir / f"generated_artwork_{timestamp}.png"
            
            # Download image
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Save image
            with open(image_path, 'wb') as f:
                f.write(response.content)

            return {
                'image_path': str(image_path),
                'prompt_used': final_prompt
            }

        except Exception as e:
            raise Exception(f"Error in DALL-E image generation: {str(e)}")

    def analyze_and_generate_art(self, file_path):
        """Complete analysis and art generation pipeline."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'input_file': file_path
        }
        
        try:
            # Read lyrics
            lyrics = self.read_lyrics(file_path)
            results['original_lyrics'] = lyrics
            
            # Get Arabic sentiment
            sentiment = self.get_arabic_sentiment(lyrics)
            results['arabic_sentiment'] = sentiment
            
            # Get GPT analysis
            gpt_analysis = self.analyze_with_gpt(lyrics)
            results['detailed_analysis'] = gpt_analysis
            
            # Generate art prompt
            art_prompt = self.generate_art_prompt(lyrics, gpt_analysis)
            results['art_prompt'] = art_prompt
            
            # Generate image with DALL-E
            image_result = self.generate_image_with_dalle(art_prompt)
            results['generated_image'] = image_result
            
            # Save analysis results
            self.save_analysis_results(results)
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            self.save_analysis_results(results)
            raise

    def save_analysis_results(self, results):
        """Save analysis results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = self.output_dir / f"analysis_results_{timestamp}.json"
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

def main():
    # Get API key from environment variable for security
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    # Initialize generator
    generator = LyricArtGenerator(api_key)
    
    # Analyze lyrics and generate art
    try:
        results = generator.analyze_and_generate_art("feiruz - Le Beirut.txt")
        
        # Print results summary
        print("\n=== Analysis and Generation Complete ===")
        print(f"Input file: {results['input_file']}")
        print(f"Sentiment: {results['arabic_sentiment']}")
        print(f"\nGenerated Image saved to: {results['generated_image']['image_path']}")
        print(f"Final prompt used: {results['generated_image']['prompt_used']}")
        print(f"\nFull analysis results saved to: {generator.output_dir}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Check the generated analysis_results JSON file for details.")