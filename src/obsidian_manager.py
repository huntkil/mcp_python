"""
Obsidian Vault Manager for MCP Server

This module provides functionality to interact with local Obsidian vaults,
including reading, creating, updating, and deleting notes, as well as
managing vault structure and metadata.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .utils import extract_frontmatter

logger = logging.getLogger(__name__)


class ObsidianManager:
    """Manages Obsidian vault operations including notes, attachments, and metadata."""

    def __init__(self, vault_path: str):
        """
        Initialize Obsidian manager with vault path.

        Args:
            vault_path: Path to the Obsidian vault directory
        """
        self.vault_path = Path(vault_path).resolve()
        self.attachments_path = self.vault_path / "attachments"
        self.templates_path = self.vault_path / "templates"

        # Ensure vault exists
        if not self.vault_path.exists():
            raise ValueError(f"Obsidian vault not found at: {self.vault_path}")

        # Create necessary directories
        self.attachments_path.mkdir(exist_ok=True)
        self.templates_path.mkdir(exist_ok=True)

        logger.info(f"ObsidianManager initialized with vault: {self.vault_path}")

    def get_vault_info(self) -> Dict[str, Any]:
        """
        Get information about the Obsidian vault.

        Returns:
            Dictionary containing vault information
        """
        try:
            # Count files
            md_files = list(self.vault_path.rglob("*.md"))
            attachment_files = (
                list(self.attachments_path.rglob("*"))
                if self.attachments_path.exists()
                else []
            )

            # Get vault size
            total_size = sum(f.stat().st_size for f in md_files if f.is_file())

            return {
                "vault_path": str(self.vault_path),
                "total_notes": len(md_files),
                "total_attachments": len(attachment_files),
                "total_size_bytes": total_size,
                "created_at": datetime.fromtimestamp(
                    self.vault_path.stat().st_ctime
                ).isoformat(),
                "last_modified": datetime.fromtimestamp(
                    self.vault_path.stat().st_mtime
                ).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting vault info: {e}")
            raise

    def list_notes(
        self, folder: str = "", recursive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List all notes in the vault or specific folder.

        Args:
            folder: Subfolder path (relative to vault root)
            recursive: Whether to search recursively

        Returns:
            List of note information dictionaries
        """
        try:
            search_path = self.vault_path / folder if folder else self.vault_path
            pattern = "**/*.md" if recursive else "*.md"

            notes = []
            for file_path in search_path.glob(pattern):
                if file_path.is_file():
                    # Get file info
                    stat = file_path.stat()
                    relative_path = file_path.relative_to(self.vault_path)

                    # Extract frontmatter if exists
                    content = file_path.read_text(encoding="utf-8")
                    frontmatter, _ = extract_frontmatter(content)

                    note_info = {
                        "filename": file_path.name,
                        "path": str(relative_path),
                        "folder": str(relative_path.parent)
                        if relative_path.parent != Path(".")
                        else "",
                        "size_bytes": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(
                            stat.st_mtime
                        ).isoformat(),
                        "frontmatter": frontmatter,
                        "has_content": len(content.strip()) > 0,
                    }
                    notes.append(note_info)

            return sorted(notes, key=lambda x: x["path"])
        except Exception as e:
            logger.error(f"Error listing notes: {e}")
            raise

    def read_note(self, note_path: str) -> Dict[str, Any]:
        """
        Read a note from the vault.

        Args:
            note_path: Path to the note (relative to vault root)

        Returns:
            Dictionary containing note content and metadata
        """
        try:
            file_path = self.vault_path / note_path

            if not file_path.exists():
                raise FileNotFoundError(f"Note not found: {note_path}")

            if not file_path.suffix == ".md":
                raise ValueError(f"File is not a markdown note: {note_path}")

            content = file_path.read_text(encoding="utf-8")
            frontmatter, body = extract_frontmatter(content)
            stat = file_path.stat()

            return {
                "path": note_path,
                "filename": file_path.name,
                "content": content,
                "body": body,
                "frontmatter": frontmatter,
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error reading note {note_path}: {e}")
            raise

    def create_note(
        self,
        note_path: str,
        content: str = "",
        frontmatter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new note in the vault.

        Args:
            note_path: Path for the new note (relative to vault root)
            content: Note content
            frontmatter: Optional frontmatter metadata

        Returns:
            Dictionary containing created note information
        """
        try:
            file_path = self.vault_path / note_path

            # Ensure .md extension
            if file_path.suffix != ".md":
                file_path = file_path.with_suffix(".md")

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare content with frontmatter
            full_content = ""
            if frontmatter:
                full_content += "---\n"
                full_content += yaml.dump(
                    frontmatter, default_flow_style=False, allow_unicode=True
                )
                full_content += "---\n\n"

            full_content += content

            # Write file
            file_path.write_text(full_content, encoding="utf-8")

            logger.info(f"Created note: {file_path}")

            return self.read_note(str(file_path.relative_to(self.vault_path)))
        except Exception as e:
            logger.error(f"Error creating note {note_path}: {e}")
            raise

    def update_note(
        self,
        note_path: str,
        content: Optional[str] = None,
        frontmatter: Optional[Dict[str, Any]] = None,
        append: bool = False,
    ) -> Dict[str, Any]:
        """
        Update an existing note.

        Args:
            note_path: Path to the note
            content: New content (if None, keeps existing)
            frontmatter: New frontmatter (if None, keeps existing)
            append: Whether to append content instead of replacing

        Returns:
            Dictionary containing updated note information
        """
        try:
            file_path = self.vault_path / note_path

            if not file_path.exists():
                raise FileNotFoundError(f"Note not found: {note_path}")

            # Read existing content
            existing_content = file_path.read_text(encoding="utf-8")
            existing_frontmatter, existing_body = extract_frontmatter(existing_content)

            # Prepare new content
            new_frontmatter = (
                frontmatter if frontmatter is not None else existing_frontmatter
            )
            new_body = content if content is not None else existing_body

            if append and content:
                new_body = existing_body + "\n\n" + content

            # Combine frontmatter and body
            full_content = ""
            if new_frontmatter:
                full_content += "---\n"
                full_content += yaml.dump(
                    new_frontmatter, default_flow_style=False, allow_unicode=True
                )
                full_content += "---\n\n"

            full_content += new_body

            # Write updated content
            file_path.write_text(full_content, encoding="utf-8")

            logger.info(f"Updated note: {file_path}")

            return self.read_note(note_path)
        except Exception as e:
            logger.error(f"Error updating note {note_path}: {e}")
            raise

    def delete_note(self, note_path: str) -> Dict[str, Any]:
        """
        Delete a note from the vault.

        Args:
            note_path: Path to the note to delete

        Returns:
            Dictionary containing deletion confirmation
        """
        try:
            file_path = self.vault_path / note_path

            if not file_path.exists():
                raise FileNotFoundError(f"Note not found: {note_path}")

            # Delete the file
            file_path.unlink()

            logger.info(f"Deleted note: {file_path}")

            return {
                "deleted": True,
                "path": note_path,
                "filename": file_path.name,
                "deleted_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error deleting note {note_path}: {e}")
            raise

    def search_notes(
        self, query: str, folder: str = "", case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for notes containing the query.

        Args:
            query: Search query
            folder: Limit search to specific folder
            case_sensitive: Whether search is case sensitive

        Returns:
            List of matching notes with search context
        """
        try:
            search_path = self.vault_path / folder if folder else self.vault_path
            matches = []

            if not case_sensitive:
                query = query.lower()

            for file_path in search_path.rglob("*.md"):
                if file_path.is_file():
                    content = file_path.read_text(encoding="utf-8")
                    search_content = content if case_sensitive else content.lower()

                    if query in search_content:
                        # Find context around matches
                        lines = content.split("\n")
                        matching_lines = []

                        for i, line in enumerate(lines):
                            search_line = line if case_sensitive else line.lower()
                            if query in search_line:
                                start = max(0, i - 2)
                                end = min(len(lines), i + 3)
                                context = lines[start:end]
                                matching_lines.append(
                                    {
                                        "line_number": i + 1,
                                        "context": context,
                                        "highlighted_line": line,
                                    }
                                )

                        relative_path = file_path.relative_to(self.vault_path)
                        stat = file_path.stat()

                        match_info = {
                            "path": str(relative_path),
                            "filename": file_path.name,
                            "folder": str(relative_path.parent)
                            if relative_path.parent != Path(".")
                            else "",
                            "matches": len(matching_lines),
                            "matching_lines": matching_lines,
                            "size_bytes": stat.st_size,
                            "modified_at": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                        matches.append(match_info)

            return sorted(matches, key=lambda x: x["path"])
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            raise

    def get_tags(self) -> Dict[str, List[str]]:
        """
        Extract all tags from the vault.

        Returns:
            Dictionary mapping tags to note paths
        """
        try:
            tags = {}

            for file_path in self.vault_path.rglob("*.md"):
                if file_path.is_file():
                    content = file_path.read_text(encoding="utf-8")
                    relative_path = str(file_path.relative_to(self.vault_path))

                    # Find tags in content (#tag format)
                    tag_pattern = r"#([a-zA-Z0-9가-힣_-]+)"
                    found_tags = re.findall(tag_pattern, content)

                    for tag in found_tags:
                        if tag not in tags:
                            tags[tag] = []
                        tags[tag].append(relative_path)

            return tags
        except Exception as e:
            logger.error(f"Error extracting tags: {e}")
            raise

    def get_links(self) -> Dict[str, List[str]]:
        """
        Extract all internal links from the vault.

        Returns:
            Dictionary mapping source notes to linked notes
        """
        try:
            links = {}

            for file_path in self.vault_path.rglob("*.md"):
                if file_path.is_file():
                    content = file_path.read_text(encoding="utf-8")
                    relative_path = str(file_path.relative_to(self.vault_path))

                    # Find internal links [[note]] format
                    link_pattern = r"\[\[([^\]]+)\]\]"
                    found_links = re.findall(link_pattern, content)

                    if found_links:
                        links[relative_path] = found_links

            return links
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            raise

    def create_template(
        self,
        template_name: str,
        content: str,
        frontmatter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a template in the templates folder.

        Args:
            template_name: Name of the template
            content: Template content
            frontmatter: Optional frontmatter for the template

        Returns:
            Dictionary containing template information
        """
        try:
            template_path = self.templates_path / f"{template_name}.md"

            # Prepare content with frontmatter
            full_content = ""
            if frontmatter:
                full_content += "---\n"
                full_content += yaml.dump(
                    frontmatter, default_flow_style=False, allow_unicode=True
                )
                full_content += "---\n\n"

            full_content += content

            # Write template
            template_path.write_text(full_content, encoding="utf-8")

            logger.info(f"Created template: {template_path}")

            return {
                "name": template_name,
                "path": str(template_path.relative_to(self.vault_path)),
                "content": full_content,
                "created_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error creating template {template_name}: {e}")
            raise

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates.

        Returns:
            List of template information
        """
        try:
            templates = []

            for template_path in self.templates_path.glob("*.md"):
                if template_path.is_file():
                    content = template_path.read_text(encoding="utf-8")
                    frontmatter, body = extract_frontmatter(content)
                    stat = template_path.stat()

                    template_info = {
                        "name": template_path.stem,
                        "path": str(template_path.relative_to(self.vault_path)),
                        "content": content,
                        "body": body,
                        "frontmatter": frontmatter,
                        "size_bytes": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(
                            stat.st_mtime
                        ).isoformat(),
                    }
                    templates.append(template_info)

            return sorted(templates, key=lambda x: x["name"])
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            raise

    def create_note_from_template(
        self,
        template_name: str,
        note_path: str,
        variables: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new note using a template.

        Args:
            template_name: Name of the template to use
            note_path: Path for the new note
            variables: Variables to substitute in the template

        Returns:
            Dictionary containing created note information
        """
        try:
            template_path = self.templates_path / f"{template_name}.md"

            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_name}")

            # Read template
            template_content = template_path.read_text(encoding="utf-8")

            # Substitute variables if provided
            if variables:
                for key, value in variables.items():
                    template_content = template_content.replace(
                        f"{{{{{key}}}}}", str(value)
                    )

            # Create note with template content
            return self.create_note(note_path, template_content)
        except Exception as e:
            logger.error(f"Error creating note from template {template_name}: {e}")
            raise
