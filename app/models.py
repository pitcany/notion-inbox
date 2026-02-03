from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class EntryType(str, Enum):
    idea = "idea"
    note = "note"
    meeting = "meeting"
    research = "research"
    task = "task"


class Project(str, Enum):
    steward = "Steward"
    tutoring = "Tutoring"
    quant = "Quant"
    personal = "Personal"
    work = "Work"


class Status(str, Enum):
    inbox = "inbox"
    triage = "triage"
    next = "next"
    done = "done"


class Source(str, Enum):
    chatgpt = "ChatGPT"
    manual = "manual"
    voice = "voice"
    web = "web"


class InboxEntry(BaseModel):
    title: str = Field(..., min_length=1)
    content: Optional[str] = None
    type: EntryType = EntryType.note
    project: Project = Project.personal
    status: Status = Status.inbox
    tags: List[str] = Field(default_factory=list)
    source: Source = Source.chatgpt
    pinned: bool = False
    also_add_to_daily_rollup: bool = False


class InboxResponse(BaseModel):
    ok: bool
    page_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    ok: bool
