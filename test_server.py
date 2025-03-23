import unittest
import requests
import json
import os
import time
import subprocess
import signal
import sys

class TestVeniceAIMCPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the server with a mock API key
        env = os.environ.copy()
        env["VENICE_API_KEY"] = "mock_api_key"
        cls.server_process = subprocess.Popen(
            ["python", "server.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Wait for server to start
        time.sleep(2)
        
    @classmethod
    def tearDownClass(cls):
        # Kill the server process
        cls.server_process.send_signal(signal.SIGTERM)
        cls.server_process.wait()
        
    def test_list_tools(self):
        response = requests.get("http://localhost:8000/mcp/tools/list")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tools", data)
        tools = [tool["name"] for tool in data["tools"]]
        self.assertIn("generate_venice_image", tools)
        self.assertIn("approve_image", tools)
        self.assertIn("regenerate_image", tools)
        self.assertIn("list_available_models", tools)
        
    def test_list_models(self):
        response = requests.post(
            "http://localhost:8000/mcp/tools/call",
            json={"tool_name": "list_available_models", "parameters": {}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("models", data)
        self.assertIn("usage_hint", data)
        self.assertTrue(len(data["models"]) > 0)
        
    def test_generate_image(self):
        response = requests.post(
            "http://localhost:8000/mcp/tools/call",
            json={"tool_name": "generate_venice_image", "parameters": {"prompt": "test image"}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("image_id", data)
        self.assertIn("image_url", data)
        self.assertIn("thumbs_up_url", data)
        self.assertIn("thumbs_down_url", data)
        self.assertIn("html", data)
        
        # Verify HTML contains hover UI elements
        html = data["html"]
        self.assertIn("venice-image-container", html)
        self.assertIn("hover-controls", html)
        self.assertIn("callApproveImage", html)
        self.assertIn("callRegenerateImage", html)
        
        # Save image_id for next tests
        return data["image_id"]
        
    def test_approve_image(self):
        # First generate an image
        image_id = self.test_generate_image()
        
        # Then approve it
        response = requests.post(
            "http://localhost:8000/mcp/tools/call",
            json={"tool_name": "approve_image", "parameters": {"image_id": image_id}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("success", data)
        self.assertTrue(data["success"])
        
    def test_regenerate_image(self):
        # First generate an image
        image_id = self.test_generate_image()
        
        # Then regenerate it
        response = requests.post(
            "http://localhost:8000/mcp/tools/call",
            json={"tool_name": "regenerate_image", "parameters": {"image_id": image_id}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("image_id", data)
        self.assertIn("image_url", data)
        self.assertIn("thumbs_up_url", data)
        self.assertIn("thumbs_down_url", data)
        self.assertIn("html", data)
        
        # Verify it's a different image ID
        self.assertNotEqual(image_id, data["image_id"])

if __name__ == "__main__":
    unittest.main()
