# Model Context Protocol (MCP) Server Wiki

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It acts as a "USB-C port for AI applications," allowing LLMs to connect to various data sources and tools in a standardized way.

## Core Architecture

MCP follows a client-server architecture:

- **MCP Hosts**: Programs like Claude Desktop, IDEs, or AI tools that want to access data through MCP
- **MCP Clients**: Protocol clients that maintain 1:1 connections with servers
- **MCP Servers**: Lightweight programs that each expose specific capabilities through the standardized Model Context Protocol
- **Local Data Sources**: Your computer's files, databases, and services that MCP servers can securely access
- **Remote Services**: External systems available over the internet (e.g., through APIs) that MCP servers can connect to

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  LLM Host   │◄────┤  MCP Server │◄────┤  External   │
│ (e.g. Claude)│     │             │     │    API     │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Key MCP Components

### 1. Tools

Tools are a powerful primitive in MCP that enable servers to expose executable functionality to clients. Through tools, LLMs can interact with external systems, perform computations, and take actions in the real world.

Key aspects of tools include:

- **Discovery**: Clients can list available tools through the `tools/list` endpoint
- **Invocation**: Tools are called using the `tools/call` endpoint, where servers perform the requested operation and return results
- **Flexibility**: Tools can range from simple calculations to complex API interactions

Each tool is defined with the following structure:
- **name**: Unique identifier for the tool
- **description**: Human-readable description of what the tool does
- **parameters**: JSON Schema defining the expected input parameters
- **returns**: JSON Schema defining the expected return value

### 2. Resources

Resources in MCP represent static or dynamic data that can be accessed by clients. Unlike tools, resources don't perform actions but provide information.

### 3. Prompts

Prompts are reusable templates that can be used to structure interactions with LLMs.

## Implementing an MCP Server

### Server Components

A typical MCP server consists of:

1. **HTTP Server**: Handles incoming requests from MCP clients
2. **Tool Definitions**: Functions that LLMs can call to interact with the server
3. **Resource Definitions**: Data that LLMs can access through the server
4. **External API Integration**: Code that interfaces with external services

### Implementation Steps

1. **Set up the HTTP server**: Create an HTTP server that implements the MCP protocol endpoints
2. **Define tools**: Create tool definitions for the functionality you want to expose
3. **Implement tool handlers**: Write the code that executes when tools are called
4. **Test the server**: Use the MCP Inspector or an MCP client to test your server

### Python Implementation with FastMCP

FastMCP is a Python library that simplifies creating MCP servers. Here's a basic example:

```python
from fastmcp import FastMCP, Tool, ToolCall

# Create the MCP server
app = FastMCP()

# Define a tool
@app.tool
def hello_world(name: str) -> str:
    """Say hello to someone.
    
    Args:
        name: The name of the person to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}!"

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Venice AI Image Generator MCP Server

For our Venice AI Image Generator MCP server, we'll implement the following tools:

1. **generate_venice_image**: Creates an image from a text prompt and returns it with approval options
2. **approve_image**: Marks an image as approved when the user gives a thumbs up
3. **regenerate_image**: Creates a new image with the same parameters when the user gives a thumbs down
4. **list_available_models**: Provides information about available Venice AI models

The server will maintain an in-memory cache to track generated images and their approval status.

## MCP Resources

- [MCP Introduction](https://modelcontextprotocol.io/introduction) - Official introduction to the Model Context Protocol
- [MCP SDKs](https://modelcontextprotocol.io/sdks) - Official SDKs for Python, TypeScript, Java, and Kotlin
- [MCP GitHub Repository](https://github.com/modelcontextprotocol) - Official MCP implementation and examples
- [Building MCP with LLMs](https://modelcontextprotocol.io/tutorials/building-mcp-with-llms) - Tutorial on using LLMs to build MCP servers
- [Example Servers](https://modelcontextprotocol.io/examples) - Gallery of official MCP server implementations
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) - Interactive debugging tool for MCP servers
