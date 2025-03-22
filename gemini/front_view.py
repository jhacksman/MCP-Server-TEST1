from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import sys
import os

def generate_front_view(image_path, output_path=None):
    """
    Generate a front view (0°) of any 3D object in the input image.
    
    Args:
        image_path: Path to the input image
        output_path: Path to save the output image (optional)
        
    Returns:
        PIL.Image: The generated front view image
    """
    # Initialize client with API key
    api_key = os.environ.get("GOOGLE_API_KEY", "AIzaSyAU-Aa-4PnpXQgWILxJwq0yGBAfhtd4p90")
    client = genai.Client(api_key=api_key)
    
    # Load input image
    input_image = Image.open(image_path)
    
    # Define the prompt for front view
    prompt = "Create a front view (0°) of this 3D object. Maintain the exact same style, colors, and proportions. Show the object facing directly forward."
    
    # Call the Gemini API
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=[prompt, input_image],
        config=types.GenerateContentConfig(
            response_modalities=["Text", "Image"]
        )
    )
    
    # Process the response
    output_image = None
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(f"Text response: {part.text}")
        elif part.inline_data is not None:
            # Decode the returned image
            output_image = Image.open(BytesIO(part.inline_data.data))
            
            # Save the image if output path is provided
            if output_path:
                output_image.save(output_path)
                print(f"Front view image saved to: {output_path}")
    
    return output_image

if __name__ == "__main__":
    # Check if image path is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python front_view.py <input_image_path> [output_image_path]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Use provided output path or create a default one
    output_path = sys.argv[2] if len(sys.argv) > 2 else "front_view_output.png"
    
    # Generate front view
    generate_front_view(input_path, output_path)
