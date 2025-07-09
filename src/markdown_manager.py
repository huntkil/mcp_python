"""
Markdown document management class for the MCP server.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

from .utils import (
    validate_file_path, ensure_directory_exists, is_markdown_file,
    extract_frontmatter, add_frontmatter, search_in_content, get_file_info
)

logger = logging.getLogger(__name__)


class MarkdownManager:
    """
    Manages Markdown documents with CRUD operations and advanced features.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the Markdown manager.
        
        Args:
            base_path: Base directory for file operations
        """
        self.base_path = Path(base_path).resolve()
        logger.info(f"MarkdownManager initialized with base path: {self.base_path}")
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Read a Markdown file and return its content.
        
        Args:
            file_path: Path to the file to read
            encoding: File encoding (default: utf-8)
            
        Returns:
            Dictionary with file content and metadata
        """
        try:
            # Validate file path
            is_valid, sanitized_path = validate_file_path(file_path, str(self.base_path))
            if not is_valid:
                return {"success": False, "error": f"Invalid file path: {sanitized_path}"}
            
            # Check if file exists
            if not Path(sanitized_path).exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Check if it's a Markdown file
            if not is_markdown_file(sanitized_path):
                return {"success": False, "error": f"Not a Markdown file: {file_path}"}
            
            # Read file content
            with open(sanitized_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Extract frontmatter
            frontmatter, content_without_frontmatter = extract_frontmatter(content)
            
            # Get file info
            file_info = get_file_info(sanitized_path)
            
            return {
                "success": True,
                "content": content,
                "content_without_frontmatter": content_without_frontmatter,
                "frontmatter": frontmatter,
                "file_info": file_info,
                "encoding": encoding
            }
            
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading file {file_path}: {e}")
            return {"success": False, "error": f"Encoding error: {e}"}
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {"success": False, "error": f"Failed to read file: {e}"}
    
    def create_file(self, file_path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Create a new Markdown file.
        
        Args:
            file_path: Path to the file to create
            content: Content to write to the file
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Validate file path
            is_valid, sanitized_path = validate_file_path(file_path, str(self.base_path))
            if not is_valid:
                return {"success": False, "error": f"Invalid file path: {sanitized_path}"}
            
            # Check if file exists and overwrite is not allowed
            if Path(sanitized_path).exists() and not overwrite:
                return {"success": False, "error": f"File already exists: {file_path}. Use overwrite=True to overwrite."}
            
            # Ensure directory exists
            if not ensure_directory_exists(sanitized_path):
                return {"success": False, "error": f"Failed to create directory for: {file_path}"}
            
            # Write file
            with open(sanitized_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created file: {sanitized_path}")
            return {
                "success": True,
                "message": f"File created successfully: {file_path}",
                "file_path": sanitized_path,
                "file_info": get_file_info(sanitized_path)
            }
            
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {e}")
            return {"success": False, "error": f"Failed to create file: {e}"}
    
    def update_file(self, file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
        """
        Update an existing Markdown file.
        
        Args:
            file_path: Path to the file to update
            content: New content
            append: Whether to append content instead of replacing
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Validate file path
            is_valid, sanitized_path = validate_file_path(file_path, str(self.base_path))
            if not is_valid:
                return {"success": False, "error": f"Invalid file path: {sanitized_path}"}
            
            # Check if file exists
            if not Path(sanitized_path).exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Read existing content if appending
            if append:
                with open(sanitized_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                new_content = existing_content + "\n\n" + content
            else:
                new_content = content
            
            # Write updated content
            with open(sanitized_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Updated file: {sanitized_path}")
            return {
                "success": True,
                "message": f"File updated successfully: {file_path}",
                "file_path": sanitized_path,
                "file_info": get_file_info(sanitized_path)
            }
            
        except Exception as e:
            logger.error(f"Error updating file {file_path}: {e}")
            return {"success": False, "error": f"Failed to update file: {e}"}
    
    def delete_file(self, file_path: str, confirm: bool = False) -> Dict[str, Any]:
        """
        Delete a Markdown file.
        
        Args:
            file_path: Path to the file to delete
            confirm: Whether to confirm deletion
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Validate file path
            is_valid, sanitized_path = validate_file_path(file_path, str(self.base_path))
            if not is_valid:
                return {"success": False, "error": f"Invalid file path: {sanitized_path}"}
            
            # Check if file exists
            if not Path(sanitized_path).exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Check if it's a Markdown file
            if not is_markdown_file(sanitized_path):
                return {"success": False, "error": f"Not a Markdown file: {file_path}"}
            
            # Delete file
            Path(sanitized_path).unlink()
            
            logger.info(f"Deleted file: {sanitized_path}")
            return {
                "success": True,
                "message": f"File deleted successfully: {file_path}"
            }
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return {"success": False, "error": f"Failed to delete file: {e}"}
    
    def list_files(self, directory: str = ".", recursive: bool = False, pattern: str = "*.md") -> Dict[str, Any]:
        """
        List Markdown files in a directory.
        
        Args:
            directory: Directory to search in
            recursive: Whether to search recursively
            pattern: File pattern to match
            
        Returns:
            Dictionary with file list
        """
        try:
            # Validate directory path
            is_valid, sanitized_path = validate_file_path(directory, str(self.base_path))
            if not is_valid:
                return {"success": False, "error": f"Invalid directory path: {sanitized_path}"}
            
            search_path = Path(sanitized_path)
            if not search_path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}
            
            if not search_path.is_dir():
                return {"success": False, "error": f"Not a directory: {directory}"}
            
            # Find files
            if recursive:
                files = list(search_path.rglob(pattern))
            else:
                files = list(search_path.glob(pattern))
            
            # Get file information
            file_list = []
            for file_path in files:
                if file_path.is_file():
                    file_info = get_file_info(str(file_path))
                    file_info["relative_path"] = str(file_path.relative_to(self.base_path))
                    file_list.append(file_info)
            
            logger.info(f"Found {len(file_list)} Markdown files in {directory}")
            return {
                "success": True,
                "files": file_list,
                "count": len(file_list),
                "directory": directory
            }
            
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return {"success": False, "error": f"Failed to list files: {e}"}
    
    def search_content(self, directory: str, query: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for content in Markdown files.
        
        Args:
            directory: Directory to search in
            query: Search query
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            Dictionary with search results
        """
        try:
            # Validate directory path
            is_valid, sanitized_path = validate_file_path(directory, str(self.base_path))
            if not is_valid:
                return {"success": False, "error": f"Invalid directory path: {sanitized_path}"}
            
            search_path = Path(sanitized_path)
            if not search_path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}
            
            if not search_path.is_dir():
                return {"success": False, "error": f"Not a directory: {directory}"}
            
            # Find all Markdown files
            markdown_files = list(search_path.rglob("*.md")) + list(search_path.rglob("*.markdown"))
            
            results = []
            for file_path in markdown_files:
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Search in content
                        matches = search_in_content(content, query, case_sensitive)
                        
                        if matches:
                            results.append({
                                "file_path": str(file_path.relative_to(self.base_path)),
                                "matches": [
                                    {"line_number": line_num, "line_content": line_content.strip()}
                                    for line_num, line_content in matches
                                ],
                                "match_count": len(matches)
                            })
                    
                    except Exception as e:
                        logger.warning(f"Error reading file {file_path}: {e}")
                        continue
            
            logger.info(f"Search completed. Found matches in {len(results)} files")
            return {
                "success": True,
                "results": results,
                "total_files_searched": len(markdown_files),
                "files_with_matches": len(results),
                "query": query,
                "case_sensitive": case_sensitive
            }
            
        except Exception as e:
            logger.error(f"Error searching content in {directory}: {e}")
            return {"success": False, "error": f"Failed to search content: {e}"}
    
    def manage_frontmatter(self, file_path: str, action: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Manage YAML frontmatter in Markdown files.
        
        Args:
            file_path: Path to the file
            action: Action to perform ('get', 'set', 'update', 'remove')
            metadata: Metadata for set/update actions
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Validate file path
            is_valid, sanitized_path = validate_file_path(file_path, str(self.base_path))
            if not is_valid:
                return {"success": False, "error": f"Invalid file path: {sanitized_path}"}
            
            # Check if file exists
            if not Path(sanitized_path).exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Read current content
            with open(sanitized_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract current frontmatter
            current_frontmatter, content_without_frontmatter = extract_frontmatter(content)
            
            if action == "get":
                return {
                    "success": True,
                    "frontmatter": current_frontmatter,
                    "has_frontmatter": current_frontmatter is not None
                }
            
            elif action == "set":
                if metadata is None:
                    return {"success": False, "error": "Metadata is required for 'set' action"}
                
                new_content = add_frontmatter(content_without_frontmatter, metadata)
                
            elif action == "update":
                if metadata is None:
                    return {"success": False, "error": "Metadata is required for 'update' action"}
                
                if current_frontmatter is None:
                    current_frontmatter = {}
                
                current_frontmatter.update(metadata)
                new_content = add_frontmatter(content_without_frontmatter, current_frontmatter)
            
            elif action == "remove":
                new_content = content_without_frontmatter
            
            else:
                return {"success": False, "error": f"Invalid action: {action}. Valid actions: get, set, update, remove"}
            
            # Write updated content
            with open(sanitized_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Frontmatter {action} completed for: {sanitized_path}")
            return {
                "success": True,
                "message": f"Frontmatter {action} completed successfully",
                "file_path": sanitized_path,
                "action": action
            }
            
        except Exception as e:
            logger.error(f"Error managing frontmatter for {file_path}: {e}")
            return {"success": False, "error": f"Failed to manage frontmatter: {e}"} 