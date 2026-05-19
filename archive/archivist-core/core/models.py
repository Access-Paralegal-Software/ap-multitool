import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Collection:
    """
    Represents an umbrella grouping of notes.
    In Evernote: A Notebook or Notebook Stack.
    In Notion: A Database or Sub-Workspace.
    In Email: An Account or Folder.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    provider_group: Optional[str] = None  # e.g. Evernote 'Stack' name
    provider: str = ""  # 'evernote', 'notion', 'email'
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "provider_group": self.provider_group,
            "provider": self.provider,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


@dataclass
class NoteAttachment:
    """
    Represents an embedded image, PDF, or file resource within a note.
    Includes property trackers for AI pre-filtering heuristic analysis.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    note_id: str = ""
    source_resource_id: Optional[str] = None  # Hash from provider
    filename: str = "unnamed_resource"
    mime_type: str = "application/octet-stream"
    file_size_bytes: int = 0
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    system_file_path: Optional[str] = None
    ai_classification: str = "untested"  # 'junk', 'valuable', 'untested'
    ai_confidence: float = 0.0
    user_approval_status: str = "pending"  # 'keep', 'discard', 'pending'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "note_id": self.note_id,
            "source_resource_id": self.source_resource_id,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "file_size_bytes": self.file_size_bytes,
            "width_px": self.width_px,
            "height_px": self.height_px,
            "system_file_path": self.system_file_path,
            "ai_classification": self.ai_classification,
            "ai_confidence": self.ai_confidence,
            "user_approval_status": self.user_approval_status
        }


@dataclass
class Note:
    """
    The central entity within Archivist Core.
    Contains full source HTML/ENML and markdown properties ready for Obsidian rendering.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: Optional[str] = None
    collection_id: Optional[str] = None
    provider: str = "evernote"
    title: str = "Untitled Note"
    
    content_raw: str = ""  # Raw ENML / HTML Source
    content_markdown: str = ""  # Normalization output
    
    source_url: Optional[str] = None
    author: Optional[str] = None
    
    original_created_at: Optional[datetime] = None
    original_updated_at: Optional[datetime] = None
    system_indexed_at: datetime = field(default_factory=datetime.now)
    
    tags: List[str] = field(default_factory=list)
    triage_status: str = "pending"  # 'pending', 'approved', 'distilled', 'trashed'
    is_distilled: bool = False
    
    attachments: List[NoteAttachment] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        import json
        return {
            "id": self.id,
            "source_id": self.source_id,
            "collection_id": self.collection_id,
            "provider": self.provider,
            "title": self.title,
            "content_raw": self.content_raw,
            "content_markdown": self.content_markdown,
            "source_url": self.source_url,
            "author": self.author,
            "original_created_at": self.original_created_at.isoformat() if self.original_created_at else None,
            "original_updated_at": self.original_updated_at.isoformat() if self.original_updated_at else None,
            "tags": json.dumps(self.tags),
            "triage_status": self.triage_status,
            "is_distilled": 1 if self.is_distilled else 0
        }
