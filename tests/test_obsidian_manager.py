"""
Unit tests for ObsidianManager.
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
import yaml

from src.obsidian_manager import ObsidianManager


class TestObsidianManager(unittest.TestCase):
    """Test cases for ObsidianManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir) / "test_vault"
        self.vault_path.mkdir()
        
        # Create test vault structure
        (self.vault_path / "attachments").mkdir()
        (self.vault_path / "templates").mkdir()
        
        self.manager = ObsidianManager(str(self.vault_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test ObsidianManager initialization."""
        self.assertEqual(self.manager.vault_path, self.vault_path)
        self.assertTrue(self.manager.attachments_path.exists())
        self.assertTrue(self.manager.templates_path.exists())
    
    def test_get_vault_info(self):
        """Test getting vault information."""
        info = self.manager.get_vault_info()
        
        self.assertIn("vault_path", info)
        self.assertIn("total_notes", info)
        self.assertIn("total_attachments", info)
        self.assertIn("total_size_bytes", info)
        self.assertEqual(info["total_notes"], 0)
        self.assertEqual(info["total_attachments"], 0)
    
    def test_create_and_read_note(self):
        """Test creating and reading a note."""
        note_path = "test_note.md"
        content = "# Test Note\n\nThis is a test note."
        frontmatter = {"title": "Test Note", "tags": ["test"]}
        
        # Create note
        created = self.manager.create_note(note_path, content, frontmatter)
        self.assertEqual(created["path"], note_path)
        self.assertIn(content, created["content"])
        
        # Read note
        read = self.manager.read_note(note_path)
        self.assertEqual(read["path"], note_path)
        self.assertEqual(read["body"], content)
        self.assertEqual(read["frontmatter"], frontmatter)
    
    def test_update_note(self):
        """Test updating a note."""
        note_path = "test_note.md"
        original_content = "# Original\n\nOriginal content."
        
        # Create note
        self.manager.create_note(note_path, original_content)
        
        # Update note
        new_content = "# Updated\n\nUpdated content."
        updated = self.manager.update_note(note_path, new_content)
        self.assertEqual(updated["body"], new_content)
        
        # Test append
        append_content = "\n\nAppended content."
        appended = self.manager.update_note(note_path, append_content, append=True)
        self.assertIn(new_content, appended["body"])
        self.assertIn(append_content, appended["body"])
    
    def test_delete_note(self):
        """Test deleting a note."""
        note_path = "test_note.md"
        content = "# Test Note\n\nContent."
        
        # Create note
        self.manager.create_note(note_path, content)
        self.assertTrue((self.vault_path / note_path).exists())
        
        # Delete note
        result = self.manager.delete_note(note_path)
        self.assertTrue(result["deleted"])
        self.assertFalse((self.vault_path / note_path).exists())
    
    def test_list_notes(self):
        """Test listing notes."""
        # Create some test notes
        self.manager.create_note("note1.md", "# Note 1")
        self.manager.create_note("note2.md", "# Note 2")
        (self.vault_path / "subfolder").mkdir()
        self.manager.create_note("subfolder/note3.md", "# Note 3")
        
        # List all notes
        notes = self.manager.list_notes()
        self.assertEqual(len(notes), 3)
        
        # List notes in subfolder
        subfolder_notes = self.manager.list_notes("subfolder")
        self.assertEqual(len(subfolder_notes), 1)
        self.assertEqual(subfolder_notes[0]["filename"], "note3.md")
    
    def test_search_notes(self):
        """Test searching notes."""
        # Create test notes
        self.manager.create_note("note1.md", "# Note 1\n\nContains keyword.")
        self.manager.create_note("note2.md", "# Note 2\n\nNo keyword here.")
        self.manager.create_note("note3.md", "# Note 3\n\nAlso contains keyword.")
        
        # Search for keyword
        results = self.manager.search_notes("keyword")
        self.assertEqual(len(results), 2)
        
        # Check search context
        for result in results:
            self.assertGreater(result["matches"], 0)
            self.assertIn("matching_lines", result)
    
    def test_get_tags(self):
        """Test extracting tags."""
        # Create notes with tags
        self.manager.create_note("note1.md", "# Note 1\n\n#tag1 #tag2")
        self.manager.create_note("note2.md", "# Note 2\n\n#tag2 #tag3")
        
        tags = self.manager.get_tags()
        self.assertIn("tag1", tags)
        self.assertIn("tag2", tags)
        self.assertIn("tag3", tags)
        self.assertEqual(len(tags["tag1"]), 1)
        self.assertEqual(len(tags["tag2"]), 2)
    
    def test_get_links(self):
        """Test extracting internal links."""
        # Create notes with links
        self.manager.create_note("note1.md", "# Note 1\n\n[[note2]] [[note3]]")
        self.manager.create_note("note2.md", "# Note 2\n\n[[note1]]")
        
        links = self.manager.get_links()
        self.assertIn("note1.md", links)
        self.assertIn("note2.md", links)
        self.assertEqual(len(links["note1.md"]), 2)
        self.assertEqual(len(links["note2.md"]), 1)
    
    def test_create_and_list_templates(self):
        """Test creating and listing templates."""
        template_name = "test_template"
        content = "# {{title}}\n\n{{content}}"
        frontmatter = {"type": "template"}
        
        # Create template
        created = self.manager.create_template(template_name, content, frontmatter)
        self.assertEqual(created["name"], template_name)
        
        # List templates
        templates = self.manager.list_templates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]["name"], template_name)
    
    def test_create_note_from_template(self):
        """Test creating a note from a template."""
        template_name = "test_template"
        content = "# {{title}}\n\n{{content}}"
        
        # Create template
        self.manager.create_template(template_name, content)
        
        # Create note from template
        variables = {"title": "My Note", "content": "This is my content."}
        note = self.manager.create_note_from_template(template_name, "my_note.md", variables)
        
        self.assertIn("My Note", note["content"])
        self.assertIn("This is my content.", note["content"])
    
    def test_note_without_extension(self):
        """Test creating note without .md extension."""
        note_path = "test_note"
        content = "# Test"
        
        created = self.manager.create_note(note_path, content)
        self.assertEqual(created["path"], "test_note.md")
        self.assertTrue((self.vault_path / "test_note.md").exists())
    
    def test_error_handling(self):
        """Test error handling."""
        # Try to read non-existent note
        with self.assertRaises(FileNotFoundError):
            self.manager.read_note("non_existent.md")
        
        # Try to delete non-existent note
        with self.assertRaises(FileNotFoundError):
            self.manager.delete_note("non_existent.md")
        
        # Try to create note from non-existent template
        with self.assertRaises(FileNotFoundError):
            self.manager.create_note_from_template("non_existent", "test.md")


if __name__ == "__main__":
    unittest.main() 