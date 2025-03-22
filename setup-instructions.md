# Venice AI MCP Server Setup Instructions

This guide provides complete instructions for setting up and running the Venice AI MCP Server, and integrating it with Claude Desktop.

## Prerequisites

- [Claude Desktop](https://claude.ai/download) installed on your computer
- [uv](https://github.com/astral-sh/uv) package manager installed
- Venice AI API key

## Step 1: Clone the Repository

```bash
git clone https://github.com/jhacksman/MCP-Server-TEST1.git
cd MCP-Server-TEST1
```

## Step 2: Set Up the Environment with uv

Create and activate a virtual environment using uv:

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

## Step 3: Install Dependencies with uv

Install the required dependencies:

```bash
uv pip install fastapi uvicorn requests
```

## Step 4: Set Your Venice API Key

Set your Venice API key as an environment variable:

```bash
# On macOS/Linux:
export VENICE_API_KEY="your_api_key_here"

# On Windows:
set VENICE_API_KEY=your_api_key_here
```

## Step 5: Run the MCP Server

Start the Venice AI MCP Server:

```bash
python server.py
```

The server will start on http://localhost:8000 with the following MCP endpoints:
- `/mcp/tools/list` - Lists available tools
- `/mcp/tools/call` - Endpoint for calling tools

## Step 6: Configure Claude Desktop

### Locate the Configuration File

The Claude Desktop configuration file is located at:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Edit the Configuration File

1. Open Claude Desktop
2. Click on the Claude menu and select "Settings..."
3. Click on "Developer" in the left sidebar
4. Click on "Edit Config"

This will open the `claude_desktop_config.json` file in your text editor.

### Add the MCP Server Configuration

Replace the contents of the file with the following configuration:

```json
{
  "mcpServers": {
    "venice-ai": {
      "url": "http://localhost:8000"
    }
  }
}
```

This configuration tells Claude Desktop to connect to your locally running Venice AI MCP Server.

## Step 7: Restart Claude Desktop

After saving the configuration file, restart Claude Desktop for the changes to take effect.

## Step 8: Verify the Integration

1. After restarting Claude Desktop, you should see a hammer icon in the bottom right corner of the input box.
2. Click on the hammer icon to see the available tools from the Venice AI MCP Server:
   - `generate_venice_image`
   - `approve_image`
   - `regenerate_image`
   - `list_available_models`

## Step 9: Try It Out

You can now ask Claude to generate images using Venice AI. Try prompts like:

- "Generate an image of a futuristic city skyline using Venice AI"
- "Show me what models are available in Venice AI"

Claude will use the MCP tools to interact with the Venice AI API and display the results.

## Troubleshooting

### 404 Not Found Error

If you see a 404 Not Found error when accessing http://localhost:8000/, this is expected. The root path (/) is not defined in the server. The MCP endpoints are:

- http://localhost:8000/mcp/tools/list
- http://localhost:8000/mcp/tools/call

Claude Desktop will automatically use these endpoints.

### Server Not Showing Up in Claude

If the hammer icon is missing or the server isn't showing up:

1. Make sure the server is running on http://localhost:8000
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

## Advanced Configuration

For more advanced configuration options, you can specify authentication, headers, or other options:

```json
{
  "mcpServers": {
    "venice-ai": {
      "url": "http://localhost:8000",
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
