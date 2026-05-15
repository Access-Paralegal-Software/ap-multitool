from abc import ABC, abstractmethod
from typing import Iterator, Any
from core.models import Note, Collection

class BaseAdapter(ABC):
    """
    Abstract Base Class defining the contract for all ingest providers.
    Every new digital brain parser must inherit from this and implement these methods.
    """

    @abstractmethod
    def parse_collection(self, source_path: str, **kwargs: Any) -> Collection:
        """
        Analyzes the source file or database path to extract the parent collection.
        In Evernote: Extracts notebook name/metadata from the filename or metadata block.
        """
        pass

    @abstractmethod
    def parse_notes(self, source_path: str, parent_collection: Collection) -> Iterator[Note]:
        """
        A generator yielding unified 'Note' objects from the raw source input.
        Must handle lazy loading/streaming to support multi-gigabyte archives without 
        exhausting system memory.
        """
        pass

    @abstractmethod
    def render_to_markdown(self, note: Note) -> str:
        """
        Takes the raw underlying markup (ENML, Rich Text, HTML) and converts it 
        into standardized Archivist Core clean Markdown format.
        """
        pass
