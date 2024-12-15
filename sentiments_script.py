from transformers import pipeline
import json
from datetime import datetime
from pathlib import Path

class LyricAnalyzer:
    def __init__(self, client, language='unspecified'):
        """Initialize with OpenAI API key and sentiment analyzer."""
        self.client = client
        
        #ISO 639-1 two-letter language codes
        if (language == 'en'):
            self.sentiment_pipeline = pipeline(
                "text-classification", 
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        elif (language == 'ar'):
            self.sentiment_pipeline = pipeline(
                "text-classification",
                model="PRAli22/AraBert-Arabic-Sentiment-Analysis"
            )
        else:
            self.sentiment_pipeline = pipeline(
                "text-classification", 
                model="distilbert-base-multilingual-cased"
            )

        self.output_dir = Path("analysis_results")
        self.output_dir.mkdir(exist_ok=True)

    def read_lyrics(self, file_path):
        """Read lyrics file with proper encoding."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp1252') as file:
                return file.read()

    def get_sentiment(self, text):
        """Get sentiment using previously determined model."""
        results = self.sentiment_pipeline(text, truncation=True)
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
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a literary expert specialized in analyzing lyrics and poetry. Provide deep, insightful analysis while maintaining objectivity."},
                    {"role": "user", "content": prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "lyrics_analysis_schema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "major_themes_and_motifs": {
                                    "description": "Analysis of major themes and motifs in the lyrics.",
                                    "type": "string"
                                },
                                "emotional_undertones": {
                                    "description": "Insight into the emotional undertones of the lyrics.",
                                    "type": "string"
                                },
                                "notable_imagery_and_metaphors": {
                                    "description": "Identification of notable imagery and metaphors.",
                                    "type": "string"
                                },
                                "cultural_or_historical_references": {
                                    "description": "Explanation of cultural or historical references in the lyrics.",
                                    "type": "string"
                                },
                                "key_symbols_and_their_significance": {
                                    "description": "Key symbols and their literary significance.",
                                    "type": "string"
                                },
                                "overall_tone_and_atmosphere": {
                                    "description": "Analysis of the overall tone and atmosphere of the lyrics.",
                                    "type": "string"
                                }
                            },
                            "required": [
                                "major_themes_and_motifs",
                                "emotional_undertones",
                                "notable_imagery_and_metaphors",
                                "cultural_or_historical_references",
                                "key_symbols_and_their_significance",
                                "overall_tone_and_atmosphere"
                            ],
                            "additionalProperties": False
                        }
                    }
                }
            )

            return response

        except Exception as e:
            raise Exception(f"Error in GPT analysis: {str(e)}")
        

    # main function to be called
    def analyze_lyrics(self,file_path):
        """Complete semantic analysis pipeline."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'input_file': file_path
        }
        
        try:
            lyrics = self.read_lyrics(file_path)
            results['original_lyrics'] = lyrics
            
            # Get English sentiment
            sentiment = self.get_sentiment(lyrics)
            results['hugging_sentiment'] = sentiment
            
            # Get GPT analysis
            gpt_analysis = self.analyze_with_gpt(lyrics)
            results['detailed_analysis'] = gpt_analysis
            
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