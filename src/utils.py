"""
Utility functions for the Markdown MCP Server.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_file_path(file_path: str, base_path: str = ".") -> Tuple[bool, str]:
    """
    Validate and sanitize file path to prevent path traversal attacks.
    
    Args:
        file_path: The file path to validate
        base_path: The base directory to restrict access to
        
    Returns:
        Tuple of (is_valid, sanitized_path)
    """
    try:
        base_path = Path(base_path).resolve()
        full_path = (base_path / file_path).resolve()
        
        # Check if the resolved path is within the base path
        if not str(full_path).startswith(str(base_path)):
            return False, "Path traversal detected"
        
        return True, str(full_path)
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return False, str(e)


def ensure_directory_exists(file_path: str) -> bool:
    """
    Ensure the directory for the given file path exists.
    
    Args:
        file_path: The file path
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        directory = Path(file_path).parent
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory: {e}")
        return False


def is_markdown_file(file_path: str) -> bool:
    """
    Check if the file is a Markdown file.
    
    Args:
        file_path: The file path
        
    Returns:
        True if it's a Markdown file
    """
    return file_path.lower().endswith(('.md', '.markdown'))


def extract_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """
    Extract YAML frontmatter from Markdown content.
    
    Args:
        content: The Markdown content
        
    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    try:
        import yaml
        
        # Check for frontmatter pattern
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            frontmatter_text = match.group(1)
            content_without_frontmatter = content[match.end():]
            
            try:
                frontmatter = yaml.safe_load(frontmatter_text)
                return frontmatter, content_without_frontmatter
            except yaml.YAMLError as e:
                logger.warning(f"Invalid YAML frontmatter: {e}")
                return None, content
        else:
            return None, content
            
    except ImportError:
        logger.warning("PyYAML not available, frontmatter extraction disabled")
        return None, content


def add_frontmatter(content: str, metadata: Dict) -> str:
    """
    Add YAML frontmatter to Markdown content.
    
    Args:
        content: The Markdown content
        metadata: The metadata to add as frontmatter
        
    Returns:
        Content with frontmatter added
    """
    try:
        import yaml
        
        frontmatter_text = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        return f"---\n{frontmatter_text}---\n\n{content}"
        
    except ImportError:
        logger.warning("PyYAML not available, frontmatter addition disabled")
        return content


def search_in_content(content: str, query: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
    """
    Search for a query in content and return matching lines.
    
    Args:
        content: The content to search in
        query: The search query
        case_sensitive: Whether the search should be case sensitive
        
    Returns:
        List of tuples (line_number, line_content)
    """
    matches = []
    lines = content.split('\n')
    
    flags = 0 if case_sensitive else re.IGNORECASE
    
    for i, line in enumerate(lines, 1):
        if re.search(query, line, flags):
            matches.append((i, line))
    
    return matches


def get_file_info(file_path: str) -> Dict:
    """
    Get information about a file.
    
    Args:
        file_path: The file path
        
    Returns:
        Dictionary with file information
    """
    try:
        path = Path(file_path)
        stat = path.stat()
        
        return {
            "name": path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "exists": path.exists()
        }
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        return {"error": str(e)}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to make it safe for file system operations.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    sanitized = filename
    
    for char in unsafe_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """
    Parse YAML frontmatter from content (alias for extract_frontmatter).
    
    Args:
        content: The content to parse
        
    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    return extract_frontmatter(content) 