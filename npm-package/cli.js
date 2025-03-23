#!/usr/bin/env node

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const chalk = require('chalk');
const yargs = require('yargs/helpers');
const { hideBin } = require('yargs/helpers');

const argv = require('yargs')(hideBin(process.argv))
  .option('port', {
    alias: 'p',
    description: 'Port to run the MCP server on',
    type: 'number',
    default: 8000
  })
  .option('api-key', {
    alias: 'k',
    description: 'Venice AI API key',
    type: 'string'
  })
  .help()
  .alias('help', 'h')
  .argv;

// Create a proxy server to forward requests to the Python server
const app = express();
const PORT = argv.port || 8000;

// Start the Python server
console.log(chalk.blue('Starting Venice AI MCP Server...'));

// Set environment variables for the Python process
const env = { ...process.env };
if (argv.apiKey) {
  env.VENICE_API_KEY = argv.apiKey;
  console.log(chalk.green('Using provided Venice AI API key'));
} else if (!process.env.VENICE_API_KEY) {
  console.log(chalk.yellow('Warning: No Venice API key provided. Set with --api-key or VENICE_API_KEY environment variable'));
}

// Determine the path to the Python script
// When installed globally, the package will be in node_modules
// When run with npx, we need to use the current directory
const serverPath = path.join(__dirname, 'server.py');

// Start the Python server
const pythonProcess = spawn('python', [serverPath], {
  env,
  stdio: ['ignore', 'pipe', 'pipe']
});

// Handle Python server output
pythonProcess.stdout.on('data', (data) => {
  console.log(chalk.cyan(`[Python] ${data.toString().trim()}`));
});

pythonProcess.stderr.on('data', (data) => {
  console.error(chalk.red(`[Python Error] ${data.toString().trim()}`));
});

// Handle Python server exit
pythonProcess.on('close', (code) => {
  if (code !== 0) {
    console.error(chalk.red(`Python server exited with code ${code}`));
    process.exit(code);
  }
});

// Forward all requests to the Python server
app.all('*', (req, res) => {
  res.status(404).send('Please use the Python server directly at http://localhost:' + PORT);
});

// Start the proxy server
app.listen(PORT + 1, () => {
  console.log(chalk.green(`
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  Venice AI Images MCP Server is running!                   ║
║                                                            ║
║  - MCP Server URL: http://localhost:${PORT}                 ║
║  - MCP Tools List: http://localhost:${PORT}/mcp/tools/list  ║
║  - MCP Tools Call: http://localhost:${PORT}/mcp/tools/call  ║
║                                                            ║
║  Claude Desktop Configuration:                             ║
║  {                                                         ║
║    "mcpServers": {                                         ║
║      "venice-ai": {                                        ║
║        "url": "http://localhost:${PORT}"                   ║
║      }                                                     ║
║    }                                                       ║
║  }                                                         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
`));
  console.log(chalk.blue('Press Ctrl+C to stop the server'));
});

// Handle process termination
process.on('SIGINT', () => {
  console.log(chalk.yellow('\nShutting down Venice AI MCP Server...'));
  pythonProcess.kill();
  process.exit(0);
});
