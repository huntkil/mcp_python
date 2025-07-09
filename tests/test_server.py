"""
Integration tests for MCP server.
"""

import unittest
import tempfile
import os
import asyncio
import json
from unittest.mock import patch, MagicMock

from src.server import MarkdownMCPServer


class TestMarkdownMCPServer(unittest.TestCase):
    """Test cases for MarkdownMCPServer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.server = MarkdownMCPServer(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_server_initialization(self):
        """Test server initialization."""
        self.assertIsNotNone(self.server.server)
        self.assertIsNotNone(self.server.markdown_manager)
        self.assertEqual(str(self.server.markdown_manager.base_path), self.temp_dir)
    
    def test_tools_registration(self):
        """Test that tools are properly registered."""
        # This is a basic test to ensure the server has the expected structure
        # In a real scenario, you would test the actual MCP protocol communication
        
        # Check that the server has the list_tools method
        self.assertTrue(hasattr(self.server.server, 'list_tools'))
        self.assertTrue(hasattr(self.server.server, 'call_tool'))
    
    @patch('src.server.types')
    def test_tool_schemas(self, mock_types):
        """Test tool schema definitions."""
        # Mock the types module
        mock_tool = MagicMock()
        mock_types.Tool = mock_tool
        
        # This test would verify that tool schemas are properly defined
        # In a real implementation, you would check the actual schema structure
        
        # For now, we'll just verify the server can be created without errors
        self.assertIsNotNone(self.server)
    
    def test_markdown_manager_integration(self):
        """Test integration with MarkdownManager."""
        # Test that the server's markdown manager works correctly
        test_file = os.path.join(self.temp_dir, "test.md")
        content = "# Test Document\n\nThis is a test."
        
        # Create a file using the manager
        result = self.server.markdown_manager.create_file(test_file, content)
        self.assertTrue(result["success"])
        
        # Read the file
        result = self.server.markdown_manager.read_file(test_file)
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], content)


class TestServerTools(unittest.TestCase):
    """Test individual tool functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.server = MarkdownMCPServer(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_markdown_tool(self):
        """Test create_markdown tool functionality."""
        # This would test the actual tool call handling
        # In a real scenario, you would simulate the MCP protocol
        
        test_file = "test.md"
        content = "# Test Document\n\nThis is a test."
        
        # Test the underlying functionality
        result = self.server.markdown_manager.create_file(test_file, content)
        self.assertTrue(result["success"])
        
        # Verify file was created
        full_path = os.path.join(self.temp_dir, test_file)
        self.assertTrue(os.path.exists(full_path))
    
    def test_read_markdown_tool(self):
        """Test read_markdown tool functionality."""
        test_file = "test.md"
        content = "# Test Document\n\nThis is a test."
        
        # Create a file first
        self.server.markdown_manager.create_file(test_file, content)
        
        # Test reading
        result = self.server.markdown_manager.read_file(test_file)
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], content)
    
    def test_search_markdown_tool(self):
        """Test search_markdown tool functionality."""
        # Create test files
        files_content = {
            "file1.md": "# File 1\n\nContains python code.",
            "file2.md": "# File 2\n\nContains JavaScript code.",
            "file3.md": "# File 3\n\nContains no specific keywords."
        }
        
        for filename, content in files_content.items():
            self.server.markdown_manager.create_file(filename, content)
        
        # Test search
        result = self.server.markdown_manager.search_content(".", "python", case_sensitive=False)
        self.assertTrue(result["success"])
        self.assertEqual(result["files_with_matches"], 1)
    
    def test_list_markdown_files_tool(self):
        """Test list_markdown_files tool functionality."""
        # Create test files
        files = ["test1.md", "test2.md", "test3.txt"]
        
        for filename in files:
            self.server.markdown_manager.create_file(filename, "# Test content")
        
        # Test listing
        result = self.server.markdown_manager.list_files(".", recursive=False)
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)  # Only markdown files
    
    def test_manage_frontmatter_tool(self):
        """Test manage_frontmatter tool functionality."""
        test_file = "test.md"
        content_with_frontmatter = """---
title: Test Document
author: Test Author
---

# Test Document

This is the content.
"""
        
        # Create file with frontmatter
        self.server.markdown_manager.create_file(test_file, content_with_frontmatter)
        
        # Test getting frontmatter
        result = self.server.markdown_manager.manage_frontmatter(test_file, "get")
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["frontmatter"])
        self.assertEqual(result["frontmatter"]["title"], "Test Document")


if __name__ == "__main__":
    unittest.main() 