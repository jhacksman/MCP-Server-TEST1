import os
import requests

def generate_image(prompt, height=1024, width=1024, steps=20, model="fluently-xl"):
    """
    Generate an image using the Venice AI API.
    
    Args:
        prompt (str): The prompt describing the image to generate
        height (int): Image height in pixels
        width (int): Image width in pixels
        steps (int): Number of diffusion steps
        model (str): Model to use for generation
        
    Returns:
        dict: The API response containing image data
    """
    url = "https://api.venice.ai/api/v1/image/generate"
    
    payload = {
        "height": height,
        "width": width,
        "steps": steps,
        "return_binary": False,
        "hide_watermark": True,
        "format": "png",
        "embed_exif_metadata": False,
        "model": model,
        "prompt": prompt
    }
    
    # Get API key from environment variable or use default for testing
    api_key = os.environ.get("VENICE_API_KEY", "B9Y68yQgatQw8wmpmnIMYcGip1phCt-43CS0OktZU6")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.request("POST", url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    # Example usage
    result = generate_image("A low-poly rabbit with black background. 3d file")
    print(result)
