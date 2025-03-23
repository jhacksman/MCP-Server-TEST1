# Claude Desktop Integration Guide for Venice AI MCP Server

This guide explains how to integrate the Venice AI MCP Server with Claude Desktop, allowing Claude to generate, approve, and regenerate images using the Venice AI API.

## Prerequisites

1. [Claude Desktop](https://claude.ai/download) installed on your computer (macOS or Windows)
2. [uv](https://github.com/astral-sh/uv) package manager installed
3. Venice AI API key

## Step 1: Install and Run the Venice AI MCP Server

First, you need to install and run the Venice AI MCP Server:

```bash
# Clone the repository
git clone https://github.com/jhacksman/MCP-Server-TEST1.git
cd MCP-Server-TEST1

# Create and activate a virtual environment with uv
uv venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies with uv
uv pip install fastapi uvicorn requests

# Set your Venice API key
# On macOS/Linux:
export VENICE_API_KEY="your_api_key_here"
# On Windows:
set VENICE_API_KEY=your_api_key_here

# Run the server
python server.py
```

The server will start on http://127.0.0.1:8000 with the following MCP endpoints:
- `/mcp/tools/list` - Lists available tools
- `/mcp/tools/call` - Endpoint for calling tools

**Note**: The root path (/) is not defined in the server, so accessing http://127.0.0.1:8000/ directly will return a 404 Not Found error. This is expected behavior. Claude Desktop will automatically use the correct MCP endpoints.

## Step 2: Configure Claude Desktop

### Locate the Configuration File

The Claude Desktop configuration file is located at:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

You can access this file in several ways:

#### Method 1: Through Claude Desktop Settings

1. Open Claude Desktop
2. Click on the Claude menu and select "Settings..."
3. Click on "Developer" in the left sidebar
4. Click on "Edit Config"

#### Method 2: Direct File Access

Navigate to the file location using your file explorer:

- **macOS**: Open Finder, press Cmd+Shift+G, and enter `~/Library/Application Support/Claude/`
- **Windows**: Press Win+R, type `%APPDATA%\Claude\`, and press Enter

### Step 3: Edit the Configuration File

Replace the contents of the file with the following configuration:

```json
{
  "mcpServers": {
    "venice-ai": {
      "url": "http://127.0.0.1:8000"
    }
  }
}
```

This configuration tells Claude Desktop to connect to your locally running Venice AI MCP Server.

#### For Windows WSL Users

If you're running the server in WSL but using Claude Desktop in Windows, use this configuration instead:

```json
{
  "mcpServers": {
    "venice-ai": {
      "url": "http://127.0.0.1:8000"
    }
  }
}
```

Make sure port forwarding is properly set up between WSL and Windows.

## Step 4: Restart Claude Desktop

After saving the configuration file, completely close and restart Claude Desktop for the changes to take effect.

## Step 5: Verify the Integration

1. After restarting Claude Desktop, you should see a hammer icon in the bottom right corner of the input box.
2. Click on the hammer icon to see the available tools from the Venice AI MCP Server:
   - `generate_venice_image`
   - `approve_image`
   - `regenerate_image`
   - `list_available_models`

## Step 6: Try It Out

You can now ask Claude to generate images using Venice AI. Try prompts like:

- "Generate an image of a futuristic city skyline using Venice AI"
- "Show me what models are available in Venice AI"

Claude will use the MCP tools to interact with the Venice AI API and display the results.

## Troubleshooting

### 404 Not Found Error

If you see a 404 Not Found error when accessing http://127.0.0.1:8000/, this is expected. The root path (/) is not defined in the server. The MCP endpoints are:

- http://127.0.0.1:8000/mcp/tools/list
- http://127.0.0.1:8000/mcp/tools/call

Claude Desktop will automatically use these endpoints.

### Server Not Showing Up in Claude

If the hammer icon is missing or the server isn't showing up:

1. Make sure the server is running on http://127.0.0.1:8000
2. Check that the configuration file has the correct URL
3. Restart Claude Desktop
4. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/main.log`
   - Windows: `%APPDATA%\Claude\logs\main.log`

### Tool Calls Failing

If tool calls are failing:

1. Make sure your Venice API key is set correctly
2. Check the server logs for any errors
3. Verify that the server is responding to requests at `/mcp/tools/list` and `/mcp/tools/call`

### Using MCPM for Server Management

For easier management of MCP servers, you can use [MCPM](https://github.com/MCP-Club/mcpm), a command-line tool for managing MCP servers in Claude Desktop:

```bash
# Install MCPM
npm install -g @mcp-club/mcpm

# List installed servers
mcpm list

# Add your Venice AI server
mcpm add venice-ai http://127.0.0.1:8000

# Enable the server
mcpm enable venice-ai
```

## Advanced Configuration

For more advanced configuration options, you can specify authentication, headers, or other options:

```json
{
  "mcpServers": {
    "venice-ai": {
      "url": "http://127.0.0.1:8000",
      "headers": {
        "Authorization": "Bearer your_auth_token"
      }
    }
  }
}
```

## Security Considerations

- The MCP server runs locally on your machine and is only accessible to Claude Desktop
- Claude Desktop will ask for your permission before executing any actions
- Your Venice API key is stored as an environment variable and not hardcoded in the configuration
