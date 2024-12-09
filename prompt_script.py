import json
def generate_art_prompt(client, text, analysis_results, model="gpt-3.5-turbo"):
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
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating artistic prompts that capture the essence of literary works."},
                    {"role": "user", "content": prompt}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error in prompt generation: {str(e)}")