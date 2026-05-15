import os
import re
from typing import Tuple

from core.models import NoteAttachment

class AttachmentFilterEngine:
    """
    Deterministic rules engine classifying Evernote attachments based on resolution,
    file sizes, mime-types, and string patterns. Designed to aggressively flag 
    bloated web clippings (logos, icons, spacers) before user review.
    """

    # Filename substrings heavily indicative of email signature/social/web noise
    JUNK_KEYWORDS = [
        "facebook", "twitter", "instagram", "linkedin", "pinterest", "youtube",
        "logo", "icon", "spacer", "pixel", "banner", "header", "footer", 
        "btn", "button", "nav", "avatar", "tracking", "share"
    ]

    def classify(self, attachment: NoteAttachment) -> Tuple[str, float]:
        """
        Analyzes an attachment and returns (classification, confidence_score).
        Classifications: 'junk', 'valuable', 'untested'
        """
        filename_lower = attachment.filename.lower()
        w = attachment.width_px
        h = attachment.height_px
        size = attachment.file_size_bytes
        mime = attachment.mime_type.lower()

        # --- RULE 1: PDF / Documents (Always valuable) ---
        if "pdf" in mime or "document" in mime or "msword" in mime:
            return "valuable", 1.0

        # --- RULE 2: The 'Tracking Pixel / Spacer' Trap ---
        # Exceedingly small footprint or single-pixel dimensions
        if (w is not None and w <= 5) or (h is not None and h <= 5):
            return "junk", 1.0
        if size > 0 and size < 150: # Under 150 base64 chars is almost certainly noise
            return "junk", 0.98

        # --- RULE 3: Social / App Icon Recognition ---
        # Almost all web/social icons are small squares (16x16 to 48x48)
        if w is not None and h is not None:
            if 10 <= w <= 64 and 10 <= h <= 64:
                # Check aspect ratio is roughly square
                aspect = w / h
                if 0.85 <= aspect <= 1.15:
                    return "junk", 0.92

        # --- RULE 4: Keyword Pattern Flagging ---
        for kw in self.JUNK_KEYWORDS:
            if kw in filename_lower:
                # If it's small OR width/height missing, flag it higher
                if w is not None and w < 200:
                    return "junk", 0.85
                # Even if unknown dimensions, if filename matches and size is small
                if size < 2000: # under 2KB
                    return "junk", 0.80

        # --- RULE 5: High-Value Visual Anchors ---
        # High-res images or large binaries are almost certainly user-generated photos/clips
        if (w is not None and w >= 350) and (h is not None and h >= 350):
            return "valuable", 0.95
        if size > 50000: # Larger than 50KB (approx)
            return "valuable", 0.90

        # --- FALLBACK ---
        # If we can't be sure, mark as untested but lean toward valuable to be safe
        return "untested", 0.0
