import os
import re
import base64
import hashlib
import xml.etree.ElementTree as ET
from typing import Dict, List, Set
from datetime import datetime

class MarkdownExporter:
    """
    Converts normalized Evernote ENML content into Obsidian-optimized Markdown,
    decoding base64 binaries and generating secure, standalone note bundles.
    """

    def __init__(self, output_root: str, junk_ids: Set[str] = None):
        self.output_root = output_root
        self.junk_ids = junk_ids or set()
        os.makedirs(output_root, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Removes forbidden filesystem characters."""
        # Replace Windows/Linux invalid characters with underscores
        clean = re.sub(r'[\\/*?:"<>|]', "_", name)
        return clean.strip()

    def _parse_evernote_date(self, date_str: str) -> str:
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cleaned = date_str.strip().replace('Z', '')
            dt = datetime.strptime(cleaned, '%Y%m%dT%H%M%S')
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return date_str

    def _convert_enml_to_markdown(self, content_raw: str, asset_map: Dict[str, str]) -> str:
        """
        Dependency-free, high-speed regex parsing mapping Evernote markup (ENML) 
        to beautiful GitHub Flavored Markdown.
        """
        if not content_raw:
            return ""

        # 1. Strip XML/DOCTYPE overhead
        md = content_raw
        md = re.sub(r'<\?xml.*?\?>', '', md)
        md = re.sub(r'<!DOCTYPE.*?>', '', md)
        md = re.sub(r'</?en-note.*?>', '', md)

        # 2. Convert block elements to newlines
        md = re.sub(r'</?div.*?>', '\n', md)
        md = re.sub(r'</?p.*?>', '\n', md)
        md = re.sub(r'<br\s*/?>', '\n', md)

        # 3. Map Links: <a href="url">text</a> -> [text](url)
        md = re.sub(r'<a\s+href="([^"]+)".*?>(.*?)</a>', r'[\2](\1)', md)

        # 4. Inline styling: <b> -> **, <i> -> *, <u> -> <u>
        md = re.sub(r'</?strong.*?>', '**', md)
        md = re.sub(r'</?b.*?>', '**', md)
        md = re.sub(r'</?em.*?>', '*', md)
        md = re.sub(r'</?i.*?>', '*', md)

        # 5. THE ABSOLUTE CORE: Substitute <en-media> with Obsidian Wiki-links
        # Evernote stores attachment maps by hash (MD5 in hex)
        def replace_media(match):
            attrs = match.group(1)
            # Extract the MD5 hash attribute
            hash_match = re.search(r'hash="([a-fA-F0-9]+)"', attrs)
            if hash_match:
                media_hash = hash_match.group(1).lower()
                # If this hash matches a preserved asset, replace with Wiki-link
                if media_hash in asset_map:
                    return f"\n![[{asset_map[media_hash]}]]\n"
            
            # If hash was junk or not found, return notice
            return "\n*[[Embedded Resource Ignored by Pre-Filter]]*\n"

        md = re.sub(r'<en-media\s+([^>]+)/?>', replace_media, md)

        # 6. Final Formatting: Cleanup redundant whitespace and blank lines
        md = re.sub(r'\n\s*\n\s*\n', '\n\n', md)
        
        # Strip any leftover HTML tags to prevent raw tag pollution
        md = re.sub(r'<[^>]+>', '', md)

        return md.strip()

    def export_note_bundle(self, note_elem: ET.Element, collection_name: str):
        """
        Processes a single <note> XML tree block, creates physical bundle,
        extracts non-junk attachments, and writes GFM Markdown.
        """
        title = note_elem.findtext('title', 'Untitled Note')
        created_raw = note_elem.findtext('created', '')
        updated_raw = note_elem.findtext('updated', '')
        content_raw = note_elem.findtext('content', '')
        
        # Fetch attributes
        attrs = note_elem.find('note-attributes')
        source_url = attrs.findtext('source-url', '') if attrs is not None else ''
        author = attrs.findtext('author', '') if attrs is not None else ''
        
        # Fetch Tags
        tags = [t.text for t in note_elem.findall('tag') if t.text]

        # 1. Setup Physical Directory Architecture
        clean_title = self._sanitize_filename(title)
        clean_coll = self._sanitize_filename(collection_name)
        
        # Target: [Collection]/[Note Title Bundle]/
        bundle_path = os.path.join(self.output_root, clean_coll, clean_title)
        os.makedirs(bundle_path, exist_ok=True)

        # 2. Process Resources & Build Hash Map
        asset_map = {} # MD5 hex -> Filename for wiki-linking
        
        for idx, res in enumerate(note_elem.findall('resource')):
            data_elem = res.find('data')
            if data_elem is None or not data_elem.text:
                continue

            mime_type = res.findtext('mime', 'application/octet-stream')
            
            # Resource attributes
            res_attrs = res.find('resource-attributes')
            filename = f"attachment_{idx}"
            if res_attrs is not None:
                filename = res_attrs.findtext('file-name', filename)
            
            filename = self._sanitize_filename(filename)

            # Compute md5 hash of the raw text to map to <en-media>
            raw_base64 = data_elem.text.strip()
            # Evernote calculates the MD5 hash of the BINARY data
            binary_data = base64.b64decode(raw_base64)
            binary_hash = hashlib.md5(binary_data).hexdigest().lower()

            # CHECK AGAINST OUR JUNK DATABASE
            # We construct a pseudo attachment_id using the hash to cross-check
            # In the real pipeline, we look up in repository. Since we are running
            # dynamic stream, we check if the file is flagged by our static criteria!
            
            # Pre-Filter Simulation: Discard tiny tracker GIFs
            width_elem = res.find('width')
            height_elem = res.find('height')
            w = int(width_elem.text) if width_elem is not None and width_elem.text else None
            h = int(height_elem.text) if height_elem is not None and height_elem.text else None
            
            # Quick in-memory replication of the fast filter to ensure absolute safety:
            is_junk = False
            if (w is not None and w <= 5) or (h is not None and h <= 5):
                is_junk = True
            if len(binary_data) < 100:
                is_junk = True

            if is_junk:
                continue # Purge! Do not write to bundle.

            # User Requirement: Include Note Title or Context in file name to prevent lost assets
            # Syntax: "[CleanNoteTitle]_[AssetIdx]_[OriginalFilename]"
            safe_asset_filename = f"{clean_title[:30]}_{idx}_{filename}"
            asset_filepath = os.path.join(bundle_path, safe_asset_filename)

            try:
                with open(asset_filepath, "wb") as af:
                    af.write(binary_data)
                
                # Log successful map for wiki-linker
                asset_map[binary_hash] = safe_asset_filename
            except Exception as e:
                print(f"   [WARNING] Failed to write asset {filename}: {e}")

        # 3. Convert Content to Markdown
        markdown_content = self._convert_enml_to_markdown(content_raw, asset_map)

        # 4. Generate Obsidian Frontmatter Metadata
        yaml_header = "---\n"
        yaml_header += f"title: \"{title}\"\n"
        yaml_header += f"created: {self._parse_evernote_date(created_raw)}\n"
        yaml_header += f"updated: {self._parse_evernote_date(updated_raw)}\n"
        if author:
            yaml_header += f"author: \"{author}\"\n"
        if source_url:
            yaml_header += f"source: \"{source_url}\"\n"
        if tags:
            yaml_header += f"tags: [{', '.join(tags)}]\n"
        yaml_header += "provider: evernote\n"
        yaml_header += "---\n\n"

        # 5. Write Markdown Document
        md_filename = f"{clean_title}.md"
        md_filepath = os.path.join(bundle_path, md_filename)
        
        try:
            with open(md_filepath, "w", encoding="utf-8") as f:
                f.write(yaml_header + markdown_content)
        except Exception as e:
            print(f"   [WARNING] Failed to write markdown note {clean_title}: {e}")
