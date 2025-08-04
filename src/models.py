import datetime
import uuid


class Note:
    """
    Represents a note in the system.
    Attributes:
        id (str): Unique identifier for the note.
        content (str): The content of the note.
        tags (list[str]): List of tags associated with the note.
        timestamp (datetime.datetime): Timestamp when the note was created or last modified.
    """

    def __init__(
        self,
        content: str,
        tags: list[str] = None,
        timestamp: datetime.datetime = None,
        id: str = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.tags = tags or []
        self.timestamp = timestamp or datetime.datetime.now()
