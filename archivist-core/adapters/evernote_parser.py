import os
import xml.etree.ElementTree as ET
from typing import Iterator, Any, Optional
from datetime import datetime
import base64
import hashlib

from core.models import Note, NoteAttachment, Collection
from adapters.base import BaseAdapter

class EvernoteAdapter(BaseAdapter):
    """
    Highly optimized streaming parser for Evernote .ENEX XML files.
    Uses xml.etree.ElementTree.iterparse to process notes one-by-one, 
    preventing memory exhaustion on massive notebook archives.
    """

    def parse_collection(self, source_path: str, **kwargs: Any) -> Collection:
        """
        Extracts the Evernote Notebook metadata.
        Since files are partitioned by notebook, the filename represents the Notebook Name.
        """
        filename = os.path.basename(source_path)
        notebook_name, _ = os.path.splitext(filename)
        
        # Stacks are passed optionaly if the file lives in a parent directory
        parent_dir = kwargs.get("parent_dir", None)
        stack_name = parent_dir if parent_dir else None

        return Collection(
            name=notebook_name,
            provider_group=stack_name,
            provider="evernote"
        )

    def _parse_evernote_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Converts Evernote's standard XML timestamp (e.g., '20210514T190000Z') to datetime.
        """
        if not date_str:
            return None
        try:
            # Trim format standard e.g. 20210514T190000Z
            cleaned = date_str.strip().replace('Z', '')
            return datetime.strptime(cleaned, '%Y%m%dT%H%M%S')
        except Exception:
            return None

    def parse_notes(self, source_path: str, parent_collection: Collection) -> Iterator[Note]:
        """
        Streams notes out of the target .enex file using incremental parsing.
        Yields Note dataclasses containing both attributes and inline attachments.
        """
        context = ET.iterparse(source_path, events=('end',))
        
        for event, elem in context:
            if elem.tag == 'note':
                try:
                    yield self._process_note_element(elem, parent_collection)
                finally:
                    # Crucial for memory: clear processed elements from tree
                    elem.clear()

    def _process_note_element(self, elem: ET.Element, coll: Collection) -> Note:
        """
        Extracts metadata, raw ENML content, and attachments from a single <note> XML tree block.
        """
        title = elem.findtext('title', 'Untitled Note')
        created_raw = elem.findtext('created')
        updated_raw = elem.findtext('updated')
        content = elem.findtext('content', '')
        
        # Extract Attributes
        attrs = elem.find('note-attributes')
        source_url = attrs.findtext('source-url') if attrs is not None else None
        author = attrs.findtext('author') if attrs is not None else None
        
        # Extract Tags
        tags = [t.text for t in elem.findall('tag') if t.text]
        
        note = Note(
            collection_id=coll.id,
            provider="evernote",
            title=title,
            content_raw=content,
            source_url=source_url,
            author=author,
            original_created_at=self._parse_evernote_date(created_raw),
            original_updated_at=self._parse_evernote_date(updated_raw),
            tags=tags
        )
        
        # Extract Embedded Resource Assets
        for res in elem.findall('resource'):
            attachment = self._process_resource_element(res, note.id)
            if attachment:
                note.attachments.append(attachment)
                
        return note

    def _process_resource_element(self, res: ET.Element, note_id: str) -> Optional[NoteAttachment]:
        """
        Parses base64-encoded <resource> blocks into unified NoteAttachment schemas.
        """
        data_elem = res.find('data')
        if data_elem is None or not data_elem.text:
            return None
            
        mime_type = res.findtext('mime', 'application/octet-stream')
        
        # Resource attributes (file name, dims)
        res_attrs = res.find('resource-attributes')
        filename = "unnamed_asset"
        if res_attrs is not None:
            filename = res_attrs.findtext('file-name', filename)
            
        # Width / Height (Heuristics for the Pre-Filter)
        width = None
        height = None
        width_elem = res.find('width')
        height_elem = res.find('height')
        if width_elem is not None and width_elem.text:
            width = int(width_elem.text)
        if height_elem is not None and height_elem.text:
            height = int(height_elem.text)
            
        # Calculate MD5 Hash (often used in Evernote inline body <en-media>)
        raw_data = data_elem.text.strip()
        
        return NoteAttachment(
            note_id=note_id,
            filename=filename,
            mime_type=mime_type,
            file_size_bytes=len(raw_data), # Storing base64 len for now
            width_px=width,
            height_px=height
        )

    def render_to_markdown(self, note: Note) -> str:
        """
        Stub for our highly advanced HTML-to-Markdown translation engine.
        Will replace ENML elements with clean GFM markdown.
        """
        # Core logic to be populated in Phase 3
        return f"# {note.title}\n\n[Raw ENML / Content Not Yet Converted]"
