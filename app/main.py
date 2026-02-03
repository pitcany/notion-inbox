from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import InboxEntry, InboxResponse, HealthResponse
from app.notion_client import NotionClient
from app.service import create_inbox_entry

app = FastAPI(title="Notion Inbox API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

notion = NotionClient()


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(ok=True)


@app.post("/v1/inbox", response_model=InboxResponse)
async def post_inbox_entry(entry: InboxEntry):
    return create_inbox_entry(entry, notion)
