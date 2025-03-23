# Venice AI MCP Server

A Model Context Protocol (MCP) server for Venice AI image generation that can be easily integrated with Claude Desktop.

## Installation

```bash
# Install globally
npm install -g venice-ai-images-mcp

# Or run with npx
npx venice-ai-images-mcp
```

## Usage

```bash
# Start the server with default settings
venice-ai-images-mcp

# Start with a specific port
venice-ai-images-mcp --port 8080

# Provide Venice AI API key
venice-ai-images-mcp --api-key YOUR_API_KEY

# Get help
venice-ai-images-mcp --help
```

## Claude Desktop Integration

1. Start the Venice AI MCP Server
2. Open Claude Desktop
3. Go to Settings > Developer > Edit Config
4. Add the following configuration:

```json
{
  "mcpServers": {
    "venice-ai": {
      "url": "http://localhost:8000"
    }
  }
}
```

5. Restart Claude Desktop
6. Click on the hammer icon in the input box to access Venice AI tools

## Available Tools

- `generate_venice_image`: Creates an image from a text prompt
- `approve_image`: Marks an image as approved
- `regenerate_image`: Creates a new image with the same parameters
- `list_available_models`: Provides information about available Venice AI models

## Environment Variables

- `VENICE_API_KEY`: Your Venice AI API key (can also be provided with --api-key)

## Troubleshooting

If you see a 404 Not Found error when accessing http://localhost:8000/, this is expected. The root path (/) is not defined in the server. Claude Desktop will automatically use the correct MCP endpoints:

- http://localhost:8000/mcp/tools/list
- http://localhost:8000/mcp/tools/call
