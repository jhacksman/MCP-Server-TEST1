import os
import uuid
from typing import Dict, List, Optional
from fastmcp import FastMCP, Tool, ToolCall
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from venice import generate_image

# Create the MCP server
app = FastMCP()

# In-memory cache for tracking generated images and their approval status
image_cache = {}

class ImageGenerationParams(BaseModel):
    prompt: str = Field(..., description="The prompt describing the image to generate")
    height: int = Field(1024, description="Image height in pixels")
    width: int = Field(1024, description="Image width in pixels")
    steps: int = Field(20, description="Number of diffusion steps")
    model: str = Field("fluently-xl", description="Model to use for generation")

class ImageResponse(BaseModel):
    image_id: str = Field(..., description="Unique identifier for the generated image")
    image_url: str = Field(..., description="URL of the generated image")
    thumbs_up_url: str = Field(..., description="URL to approve the image")
    thumbs_down_url: str = Field(..., description="URL to regenerate the image")

class ImageApprovalParams(BaseModel):
    image_id: str = Field(..., description="ID of the image to approve")

class ModelInfo(BaseModel):
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Human-readable model name")
    description: str = Field(..., description="Description of the model's capabilities")

class ModelsResponse(BaseModel):
    models: List[ModelInfo] = Field(..., description="List of available models")

@app.tool
def generate_venice_image(params: ImageGenerationParams) -> ImageResponse:
    """Generate an image using Venice AI based on a text prompt.
    
    This tool creates an image from the provided text prompt and returns it with
    approval options (thumbs up/down) that can be displayed to the user.
    
    Args:
        params: Parameters for image generation including prompt, dimensions, etc.
        
    Returns:
        An object containing the image URL and approval options
    """
    # Generate a unique ID for this image
    image_id = str(uuid.uuid4())
    
    # Call Venice AI API to generate the image
    response = generate_image(
        prompt=params.prompt,
        height=params.height,
        width=params.width,
        steps=params.steps,
        model=params.model
    )
    
    # Extract the image URL from the response
    if "image_url" not in response:
        raise HTTPException(status_code=500, detail="Failed to generate image")
    
    image_url = response["image_url"]
    
    # Store the image details in the cache
    image_cache[image_id] = {
        "prompt": params.prompt,
        "height": params.height,
        "width": params.width,
        "steps": params.steps,
        "model": params.model,
        "image_url": image_url,
        "approved": False
    }
    
    # Create approval URLs
    # In a real implementation, these would be actual URLs that the user can click
    # For this example, we'll use placeholder URLs that include the image ID
    thumbs_up_url = f"https://example.com/approve/{image_id}"
    thumbs_down_url = f"https://example.com/regenerate/{image_id}"
    
    return ImageResponse(
        image_id=image_id,
        image_url=image_url,
        thumbs_up_url=thumbs_up_url,
        thumbs_down_url=thumbs_down_url
    )

@app.tool
def approve_image(params: ImageApprovalParams) -> Dict[str, str]:
    """Mark an image as approved when the user gives a thumbs up.
    
    Args:
        params: Parameters containing the image ID to approve
        
    Returns:
        A confirmation message
    """
    image_id = params.image_id
    
    # Check if the image exists in the cache
    if image_id not in image_cache:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Mark the image as approved
    image_cache[image_id]["approved"] = True
    
    return {"message": f"Image {image_id} has been approved"}

@app.tool
def regenerate_image(params: ImageApprovalParams) -> ImageResponse:
    """Create a new image with the same parameters when the user gives a thumbs down.
    
    Args:
        params: Parameters containing the image ID to regenerate
        
    Returns:
        A new image with approval options
    """
    image_id = params.image_id
    
    # Check if the image exists in the cache
    if image_id not in image_cache:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Get the original parameters
    original_params = image_cache[image_id]
    
    # Generate a new image with the same parameters
    return generate_venice_image(ImageGenerationParams(
        prompt=original_params["prompt"],
        height=original_params["height"],
        width=original_params["width"],
        steps=original_params["steps"],
        model=original_params["model"]
    ))

@app.tool
def list_available_models() -> ModelsResponse:
    """Provide information about available Venice AI models.
    
    Returns:
        A list of available models with their details
    """
    # In a real implementation, this would fetch the actual list of models from Venice AI
    # For this example, we'll return a static list
    models = [
        ModelInfo(
            id="fluently-xl",
            name="Fluently XL",
            description="High-quality image generation model with excellent detail and composition"
        ),
        ModelInfo(
            id="fluently-base",
            name="Fluently Base",
            description="Standard image generation model with good quality and faster generation"
        ),
        ModelInfo(
            id="fluently-creative",
            name="Fluently Creative",
            description="Model optimized for creative and artistic image generation"
        )
    ]
    
    return ModelsResponse(models=models)

# Create a FastAPI app that includes the MCP server
fastapi_app = FastAPI(title="Venice AI Image Generator MCP Server")

# Mount the MCP server at the /mcp path
fastapi_app.mount("/mcp", app)

# Add a simple health check endpoint
@fastapi_app.get("/health")
def health_check():
    return {"status": "healthy"}

# Add an endpoint to view the image cache (for debugging)
@fastapi_app.get("/debug/cache")
def view_cache():
    return JSONResponse(content=image_cache)

if __name__ == "__main__":
    # Run the server
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
