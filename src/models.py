import datetime
import uuid

class Note:
    def __init__(self, content: str, tags: list[str] = None, timestamp: datetime.datetime = None, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.tags = tags or []
        self.timestamp = timestamp or datetime.datetime.now()
