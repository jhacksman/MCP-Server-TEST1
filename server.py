import os
import uuid
import json
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from venice import generate_image

# Create the FastAPI app
app = FastAPI(title="Venice AI Image Generator MCP Server")

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

# MCP Tool definitions
MCP_TOOLS = [
    {
        "name": "generate_venice_image",
        "description": "Generate an image using Venice AI based on a text prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt describing the image to generate"
                },
                "height": {
                    "type": "integer",
                    "description": "Image height in pixels",
                    "default": 1024
                },
                "width": {
                    "type": "integer",
                    "description": "Image width in pixels",
                    "default": 1024
                },
                "steps": {
                    "type": "integer",
                    "description": "Number of diffusion steps",
                    "default": 20
                },
                "model": {
                    "type": "string",
                    "description": "Model ID to use for generation (optional). If not specified, the default model will be used. Call list_available_models to see all options.",
                    "default": "fluently-xl"
                }
            },
            "required": ["prompt"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "image_id": {
                    "type": "string",
                    "description": "Unique identifier for the generated image"
                },
                "image_url": {
                    "type": "string",
                    "description": "URL of the generated image"
                },
                "thumbs_up_url": {
                    "type": "string",
                    "description": "URL to approve the image"
                },
                "thumbs_down_url": {
                    "type": "string",
                    "description": "URL to regenerate the image"
                },
                "html": {
                    "type": "string",
                    "description": "HTML with hover-based thumbs up/down UI for the image"
                }
            }
        }
    },
    {
        "name": "approve_image",
        "description": "Mark an image as approved when the user gives a thumbs up",
        "parameters": {
            "type": "object",
            "properties": {
                "image_id": {
                    "type": "string",
                    "description": "ID of the image to approve"
                }
            },
            "required": ["image_id"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Confirmation message"
                }
            }
        }
    },
    {
        "name": "regenerate_image",
        "description": "Create a new image with the same parameters when the user gives a thumbs down",
        "parameters": {
            "type": "object",
            "properties": {
                "image_id": {
                    "type": "string",
                    "description": "ID of the image to regenerate"
                }
            },
            "required": ["image_id"]
        },
        "returns": {
            "type": "object",
            "properties": {
                "image_id": {
                    "type": "string",
                    "description": "Unique identifier for the generated image"
                },
                "image_url": {
                    "type": "string",
                    "description": "URL of the generated image"
                },
                "thumbs_up_url": {
                    "type": "string",
                    "description": "URL to approve the image"
                },
                "thumbs_down_url": {
                    "type": "string",
                    "description": "URL to regenerate the image"
                },
                "html": {
                    "type": "string",
                    "description": "HTML with hover-based thumbs up/down UI for the image"
                }
            }
        }
    },
    {
        "name": "list_available_models",
        "description": "Provide information about available Venice AI models",
        "parameters": {
            "type": "object",
            "properties": {}
        },
        "returns": {
            "type": "object",
            "properties": {
                "models": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Model identifier"
                            },
                            "name": {
                                "type": "string",
                                "description": "Human-readable model name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the model's capabilities"
                            }
                        }
                    }
                }
            }
        }
    }
]

# MCP endpoints
@app.get("/mcp/tools/list")
async def list_tools():
    """List all available MCP tools."""
    return {"tools": MCP_TOOLS}

@app.post("/mcp/tools/call")
async def call_tool(request: Request):
    """Call an MCP tool with the provided parameters."""
    try:
        data = await request.json()
        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {})
        
        if not tool_name:
            return JSONResponse(status_code=400, content={"error": "Missing tool_name"})
        
        # Call the appropriate tool function
        if tool_name == "generate_venice_image":
            return await generate_venice_image(parameters)
        elif tool_name == "approve_image":
            return await approve_image(parameters)
        elif tool_name == "regenerate_image":
            return await regenerate_image(parameters)
        elif tool_name == "list_available_models":
            return await list_available_models()
        else:
            return JSONResponse(status_code=404, content={"error": f"Tool {tool_name} not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Tool implementations
async def generate_venice_image(params):
    """Generate an image using Venice AI based on a text prompt."""
    # Generate a unique ID for this image
    image_id = str(uuid.uuid4())
    
    # Get the model from parameters
    model = params.get("model", "fluently-xl")
    
    # Validate model exists if a specific model was requested
    if "model" in params:
        try:
            # Try to fetch available models
            models_response = await list_available_models()
            available_models = [m["id"] for m in models_response.get("models", [])]
            
            if model not in available_models:
                # If model doesn't exist, return helpful error and suggest using default
                return JSONResponse(
                    status_code=400, 
                    content={
                        "error": f"Model '{model}' not found. Use list_available_models to see available options or omit the model parameter to use the default model."
                    }
                )
        except Exception as e:
            # If we can't validate, log but continue with requested model
            print(f"Warning: Could not validate model '{model}': {str(e)}")
    
    # Call Venice AI API to generate the image
    response = generate_image(
        prompt=params.get("prompt"),
        height=params.get("height", 1024),
        width=params.get("width", 1024),
        steps=params.get("steps", 20),
        model=model
    )
    
    # Extract the image URL from the response
    print("Venice API Response:", response)  # Debug print
    
    # For testing purposes, if the API fails, use a placeholder image
    if "image_url" not in response:
        # Use a placeholder image URL for testing
        image_url = "https://placehold.co/600x400?text=Venice+AI+Image"
    else:
        image_url = response["image_url"]
    
    # Store the image details in the cache
    image_cache[image_id] = {
        "prompt": params.get("prompt"),
        "height": params.get("height", 1024),
        "width": params.get("width", 1024),
        "steps": params.get("steps", 20),
        "model": params.get("model", "fluently-xl"),
        "image_url": image_url,
        "approved": False
    }
    
    # Create approval URLs
    # These URLs will be used for the API calls
    thumbs_up_url = f"/mcp/tools/call?tool_name=approve_image&image_id={image_id}"
    thumbs_down_url = f"/mcp/tools/call?tool_name=regenerate_image&image_id={image_id}"
    
    # Create HTML with thumbs up/down buttons that appear on hover
    html_wrapper = f"""
    <div class="venice-image-container" style="position: relative; display: inline-block;">
        <img src="{image_url}" alt="Generated image" style="max-width: 100%; height: auto;" />
        <div class="hover-controls" style="position: absolute; bottom: 10px; right: 10px; display: none; background-color: rgba(0,0,0,0.5); border-radius: 5px; padding: 5px;">
            <a href="#" onclick="callApproveImage('{image_id}'); return false;" style="margin-right: 10px; font-size: 24px; text-decoration: none;">👍</a>
            <a href="#" onclick="callRegenerateImage('{image_id}'); return false;" style="font-size: 24px; text-decoration: none;">👎</a>
        </div>
        <style>
            .venice-image-container:hover .hover-controls {{
                display: flex !important;
            }}
        </style>
        <script>
            function callApproveImage(id) {{
                fetch('/mcp/tools/call', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        "tool_name": "approve_image",
                        "parameters": {{"image_id": id}}
                    }})
                }});
            }}
            function callRegenerateImage(id) {{
                fetch('/mcp/tools/call', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        "tool_name": "regenerate_image",
                        "parameters": {{"image_id": id}}
                    }})
                }});
            }}
        </script>
    </div>
    """
    
    return {
        "image_id": image_id,
        "image_url": image_url,
        "thumbs_up_url": thumbs_up_url,
        "thumbs_down_url": thumbs_down_url,
        "html": html_wrapper
    }

async def approve_image(params):
    """Mark an image as approved when the user gives a thumbs up."""
    image_id = params.get("image_id")
    
    # Check if the image exists in the cache
    if image_id not in image_cache:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Mark the image as approved
    image_cache[image_id]["approved"] = True
    
    return {"message": f"Image {image_id} has been approved", "success": True}

async def regenerate_image(params):
    """Create a new image with the same parameters when the user gives a thumbs down."""
    image_id = params.get("image_id")
    
    # Check if the image exists in the cache
    if image_id not in image_cache:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Get the original parameters
    original_params = image_cache[image_id]
    
    # Generate a new image with the same parameters
    return await generate_venice_image({
        "prompt": original_params["prompt"],
        "height": original_params["height"],
        "width": original_params["width"],
        "steps": original_params["steps"],
        "model": original_params["model"]
    })

async def list_available_models():
    """Provide information about available Venice AI models."""
    try:
        # Attempt to fetch models from the Venice AI API
        api_key = os.environ.get("VENICE_API_KEY")
        if not api_key:
            raise ValueError("VENICE_API_KEY environment variable is not set")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Import requests here to avoid global import if not needed
        import requests
        
        # Use the correct endpoint for Venice AI image models
        response = requests.get("https://api.venice.ai/api/v1/models?type=image", headers=headers)
        response.raise_for_status()
        
        # Parse and return models from the API response
        models_data = response.json()
        return {
            "models": models_data,
            "usage_hint": "To use a model, call generate_venice_image with the model ID in the model parameter."
        }
        
    except Exception as e:
        # Fallback to static list if API call fails
        print(f"Error fetching models from API: {str(e)}")
        # Return the existing fallback models
        models = [
            {
                "id": "fluently-xl",
                "name": "Fluently XL",
                "description": "High-quality image generation model with excellent detail and composition"
            },
            {
                "id": "fluently-base",
                "name": "Fluently Base",
                "description": "Standard image generation model with good quality and faster generation"
            },
            {
                "id": "fluently-creative",
                "name": "Fluently Creative",
                "description": "Model optimized for creative and artistic image generation"
            }
        ]
        
        return {
            "models": models,
            "usage_hint": "To use a model, call generate_venice_image with the model ID in the model parameter."
        }

# Add a simple health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Add an endpoint to view the image cache (for debugging)
@app.get("/debug/cache")
def view_cache():
    return JSONResponse(content=image_cache)

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
