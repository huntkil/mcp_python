"""
Unit tests for MarkdownManager class.
"""

import unittest
import tempfile
import os
from pathlib import Path
import json

from src.markdown_manager import MarkdownManager


class TestMarkdownManager(unittest.TestCase):
    """Test cases for MarkdownManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MarkdownManager(self.temp_dir)
        self.test_file = os.path.join(self.temp_dir, "test.md")
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_file(self):
        """Test file creation."""
        content = "# Test Document\n\nThis is a test document."
        result = self.manager.create_file(self.test_file, content)
        
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(self.test_file))
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        self.assertEqual(file_content, content)
    
    def test_create_file_with_overwrite(self):
        """Test file creation with overwrite."""
        # Create initial file
        initial_content = "# Initial Content"
        self.manager.create_file(self.test_file, initial_content)
        
        # Overwrite with new content
        new_content = "# New Content"
        result = self.manager.create_file(self.test_file, new_content, overwrite=True)
        
        self.assertTrue(result["success"])
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        self.assertEqual(file_content, new_content)
    
    def test_create_file_without_overwrite(self):
        """Test file creation without overwrite."""
        # Create initial file
        initial_content = "# Initial Content"
        self.manager.create_file(self.test_file, initial_content)
        
        # Try to create without overwrite
        new_content = "# New Content"
        result = self.manager.create_file(self.test_file, new_content, overwrite=False)
        
        self.assertFalse(result["success"])
        self.assertIn("already exists", result["error"])
    
    def test_read_file(self):
        """Test file reading."""
        content = "# Test Document\n\nThis is a test document."
        self.manager.create_file(self.test_file, content)
        
        result = self.manager.read_file(self.test_file)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], content)
        self.assertIn("file_info", result)
    
    def test_read_nonexistent_file(self):
        """Test reading non-existent file."""
        result = self.manager.read_file("nonexistent.md")
        
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])
    
    def test_update_file(self):
        """Test file updating."""
        initial_content = "# Initial Content"
        self.manager.create_file(self.test_file, initial_content)
        
        new_content = "# Updated Content"
        result = self.manager.update_file(self.test_file, new_content)
        
        self.assertTrue(result["success"])
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        self.assertEqual(file_content, new_content)
    
    def test_update_file_append(self):
        """Test file updating with append."""
        initial_content = "# Initial Content"
        self.manager.create_file(self.test_file, initial_content)
        
        additional_content = "## Additional Section\n\nThis is additional content."
        result = self.manager.update_file(self.test_file, additional_content, append=True)
        
        self.assertTrue(result["success"])
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        expected_content = initial_content + "\n\n" + additional_content
        self.assertEqual(file_content, expected_content)
    
    def test_delete_file(self):
        """Test file deletion."""
        content = "# Test Document"
        self.manager.create_file(self.test_file, content)
        
        result = self.manager.delete_file(self.test_file)
        
        self.assertTrue(result["success"])
        self.assertFalse(os.path.exists(self.test_file))
    
    def test_list_files(self):
        """Test file listing."""
        # Create some test files
        files = [
            "test1.md",
            "test2.md",
            "test3.txt",  # Non-markdown file
            "subdir/test4.md"
        ]
        
        for file_path in files:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write("# Test content")
        
        result = self.manager.list_files(self.temp_dir, recursive=True)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 3)  # Only markdown files
        
        file_names = [f["name"] for f in result["files"]]
        self.assertIn("test1.md", file_names)
        self.assertIn("test2.md", file_names)
        self.assertIn("test4.md", file_names)
        self.assertNotIn("test3.txt", file_names)
    
    def test_search_content(self):
        """Test content searching."""
        # Create test files with specific content
        files_content = {
            "file1.md": "# File 1\n\nThis file contains the word 'python'.",
            "file2.md": "# File 2\n\nThis file contains 'JavaScript'.",
            "file3.md": "# File 3\n\nThis file has no specific keywords."
        }
        
        for filename, content in files_content.items():
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        result = self.manager.search_content(self.temp_dir, "python", case_sensitive=False)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["files_with_matches"], 1)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("file1.md", result["results"][0]["file_path"])
    
    def test_manage_frontmatter(self):
        """Test frontmatter management."""
        content_with_frontmatter = """---
title: Test Document
author: Test Author
tags: [test, markdown]
---

# Test Document

This is the content.
"""
        
        self.manager.create_file(self.test_file, content_with_frontmatter)
        
        # Test getting frontmatter
        result = self.manager.manage_frontmatter(self.test_file, "get")
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["frontmatter"])
        self.assertEqual(result["frontmatter"]["title"], "Test Document")
        self.assertEqual(result["frontmatter"]["author"], "Test Author")
        
        # Test updating frontmatter
        new_metadata = {"version": "1.0", "status": "draft"}
        result = self.manager.manage_frontmatter(self.test_file, "update", new_metadata)
        
        self.assertTrue(result["success"])
        
        # Verify the update
        result = self.manager.manage_frontmatter(self.test_file, "get")
        self.assertEqual(result["frontmatter"]["version"], "1.0")
        self.assertEqual(result["frontmatter"]["status"], "draft")
        self.assertEqual(result["frontmatter"]["title"], "Test Document")  # Should still exist


if __name__ == "__main__":
    unittest.main() 