from datetime import datetime
import requests

def generate_image_with_dalle(art_prompt, client, output_dir):
    """Generate image using DALL-E based on the art prompt."""
    try:
        # Extract the main prompt and style from the art prompt
        main_prompt = art_prompt['main_prompt']
        style = ", ".join(art_prompt['style_suggestions'][:2])  # Use top 2 style suggestions
        final_prompt = f"{main_prompt} Style: {style}"

        # Generate image with DALL-E
        response = client.images.generate(
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
        image_path = f"image_results/{output_dir}_{timestamp}.png"
        
        # Download image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save image
        with open(image_path, 'wb') as f:
            f.write(response.content)

        return str(image_path)

    except Exception as e:
        raise Exception(f"Error in DALL-E image generation: {str(e)}")