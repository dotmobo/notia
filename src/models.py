import datetime
import uuid
from typing import Optional


class Note:
    """
    Represents a note in the system.
    Attributes:
        id (str): Unique identifier for the note.
        content (str): The content of the note.
        project (str): Project associated with the note.
        timestamp (datetime.datetime): Timestamp when the note was created or last modified.
    """

    def __init__(
        self,
        content: str,
        project: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        id: Optional[str] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.project = project
        self.timestamp = timestamp or datetime.datetime.now()
