# Venice AI Image Generator MCP Server

This project implements a Model Context Protocol (MCP) server that integrates with Venice AI for image generation with an approval/regeneration workflow.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It acts as a "USB-C port for AI applications," allowing LLMs to connect to various data sources and tools in a standardized way.

For more information, visit the [official MCP introduction page](https://modelcontextprotocol.io/introduction).

## Project Overview

This MCP server provides a bridge between LLMs (like Claude) and Venice AI's image generation capabilities. It enables LLMs to generate images based on text prompts and implements an interactive approval workflow with thumbs up/down feedback.

## Key Features

### Image Generation with Approval Workflow

The core functionality of this server is to:

1. Generate images using Venice AI based on text prompts
2. Display the generated image to the user with clickable thumbs up/down icons overlaid directly on the image
3. Allow users to approve the image (clicking thumbs up) or request a regeneration (clicking thumbs down)
4. Regenerate images with the same parameters if requested

### Technical Implementation

The server implements several MCP tools:

- **generate_venice_image**: Creates an image from a text prompt and returns it with approval options
- **approve_image**: Marks an image as approved when the user gives a thumbs up
- **regenerate_image**: Creates a new image with the same parameters when the user gives a thumbs down
- **list_available_models**: Provides information about available Venice AI models

### User Experience

From the user's perspective, the interaction flow is:

1. User provides a text prompt to generate an image
2. LLM calls the MCP server to generate the image
3. LLM displays the image with clickable thumbs up/down icons overlaid directly on the image
4. User clicks the thumbs up icon on the image to approve or thumbs down icon to regenerate
5. If thumbs down, the process repeats until the user approves an image

## Architecture

The server follows the MCP client-server architecture:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  LLM Host   │◄────┤  MCP Server │◄────┤  Venice AI  │
│ (e.g. Claude)│     │             │     │    API     │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

1. **LLM Host**: The application running the LLM (e.g., Claude)
2. **MCP Server**: Our server that implements the MCP protocol and connects to Venice AI
3. **Venice AI API**: The external service that generates images

## Implementation Details

### MCP Server Components

The server consists of:

1. **FastMCP Server**: The core server that handles MCP protocol communication
2. **Venice AI Integration**: Code that interfaces with the Venice AI API
3. **Image Cache**: In-memory storage for tracking generated images and their approval status
4. **Tool Definitions**: Functions that LLMs can call to interact with the server

### Data Flow

1. LLM receives a prompt from the user
2. LLM calls the `generate_venice_image` tool with the prompt
3. Server sends request to Venice AI API
4. Venice AI generates the image and returns a URL
5. Server caches the image details and returns the URL with approval options
6. LLM displays the image and approval options to the user
7. User selects thumbs up or thumbs down
8. LLM calls either `approve_image` or `regenerate_image` based on user selection
9. If regenerating, the process repeats from step 3

## Example Usage

When connected to an LLM like Claude, the interaction would look like:

```
User: Generate an image of a futuristic city skyline
Claude: I'll generate that image for you using Venice AI.

[Image of futuristic city skyline with clickable 👍 and 👎 icons overlaid on the image]

User: 👎 (Thumbs down)
Claude: Let me generate a new version for you.

[New image of futuristic city skyline with clickable 👍 and 👎 icons overlaid on the image]

User: 👍 (Thumbs up)
Claude: Great! I've saved this approved image for you.
```

## Gemini Integration for Multi-View Generation

After a user approves an image (by clicking the thumbs up icon), the system automatically processes the approved image through Google's Gemini API to generate multiple consistent views of the 3D object:

1. The approved Venice AI image is used as input to the Gemini view generation scripts
2. Four different views are generated sequentially:
   - Front view (0°) - Generated first
   - Right view (90°) - Generated after front view completes
   - Left view (270°) - Generated after right view completes
   - Back view (180°) - Generated after left view completes
3. Each view is displayed in a 4-up layout as it becomes available
4. Each script waits for the previous script to complete successfully before executing

This multi-view generation leverages Gemini's object consistency capabilities to create coherent representations of the 3D object from different angles while maintaining the same style, colors, and proportions as the original Venice AI image.

## Future Enhancements

Potential future improvements include:

1. **Persistent Storage**: Save approved images to a database
2. **Image Editing**: Allow users to request specific modifications to generated images
3. **Multiple Image Generation**: Generate several variations at once for the user to choose from
4. **Additional Views**: Generate more angles beyond the four cardinal directions

## Venice AI Integration

The server integrates with Venice AI's image generation API, which provides high-quality image generation capabilities. The API allows for:

- Generating images from text prompts
- Customizing image dimensions
- Adjusting generation parameters
- Using different models for different styles

## Getting Started

To implement this server, you would need to:

1. Install the FastMCP library
2. Set up Venice AI API credentials
3. Implement the MCP tools as described
4. Run the server and connect it to an LLM host

## MCP Resources

For more information about the Model Context Protocol and how to build MCP servers, check out these resources:

- [MCP Introduction](https://modelcontextprotocol.io/introduction) - Official introduction to the Model Context Protocol
- [MCP SDKs](https://modelcontextprotocol.io/sdks) - Official SDKs for Python, TypeScript, Java, and Kotlin
- [MCP GitHub Repository](https://github.com/modelcontextprotocol) - Official MCP implementation and examples
- [Building MCP with LLMs](https://modelcontextprotocol.io/tutorials/building-mcp-with-llms) - Tutorial on using LLMs to build MCP servers
- [Example Servers](https://modelcontextprotocol.io/examples) - Gallery of official MCP server implementations
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) - Interactive debugging tool for MCP servers
