from typing import List, NoReturn, TYPE_CHECKING
import notion_client
from app.models import EntryType, Project, Status, Source, InboxEntry
from app.settings import settings
from app.exceptions import NotionAuthError, NotionNotFoundError, NotionPermissionError


if TYPE_CHECKING:
    from notion_client import Client


def _make_paragraph(lines: List[str]) -> dict:
    """Create a Notion paragraph block from accumulated lines."""
    return {
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": " ".join(lines)}}]
        },
    }


def _make_heading(level: int, text: str) -> dict:
    key = f"heading_{level}"
    return {
        "type": key,
        key: {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _make_bullet(text: str) -> dict:
    return {
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def markdown_to_blocks(text: str) -> List[dict]:
    """Convert simple Markdown text to Notion blocks."""
    blocks: List[dict] = []
    if not text or not text.strip():
        return blocks

    lines = text.split("\n")
    current_paragraph: List[str] = []

    def flush_paragraph() -> None:
        if current_paragraph:
            blocks.append(_make_paragraph(current_paragraph))
            current_paragraph.clear()

    for line in lines:
        stripped = line.rstrip()

        if not stripped:
            flush_paragraph()
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            blocks.append(_make_heading(3, stripped[4:]))
        elif stripped.startswith("## "):
            flush_paragraph()
            blocks.append(_make_heading(2, stripped[3:]))
        elif stripped.startswith("# ") and not stripped.startswith("## "):
            flush_paragraph()
            blocks.append(_make_heading(1, stripped[2:]))
        elif stripped.startswith("- "):
            flush_paragraph()
            blocks.append(_make_bullet(stripped[2:]))
        else:
            current_paragraph.append(stripped)

    flush_paragraph()
    return blocks


def chunk_blocks(blocks: List[dict], max_length: int = 2000) -> List[List[dict]]:
    """Split blocks into chunks that fit within Notion API size limits."""
    chunks: List[List[dict]] = []
    current_chunk: List[dict] = []
    current_length = 0

    for block in blocks:
        block_length = len(str(block))
        if current_length + block_length > max_length and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_length = 0
        current_chunk.append(block)
        current_length += block_length

    if current_chunk:
        chunks.append(current_chunk)

    return chunks if chunks else [[]]


def _classify_notion_error(e: Exception, resource: str = "Resource") -> NoReturn:
    """Inspect a Notion API exception and raise the appropriate typed error."""
    error_msg = str(e)
    if "Object not found" in error_msg:
        raise NotionNotFoundError(resource) from e
    if "Unauthorized" in error_msg or "401" in error_msg:
        raise NotionAuthError() from e
    if "missing permission" in error_msg.lower():
        raise NotionPermissionError(resource) from e
    raise


class NotionClient:
    def __init__(self) -> None:
        self.client: "Client" = notion_client.Client(auth=settings.notion_token)

    def create_inbox_page(self, entry: InboxEntry) -> tuple[str, str]:
        """Create a page in the inbox database.

        Returns:
            (page_id, page_url)

        Raises:
            NotionAuthError, NotionNotFoundError, NotionPermissionError
        """
        try:
            properties = {
                "Name": {"title": [{"text": {"content": entry.title}}]},
                "Type": {"select": {"name": entry.type.value}},
                "Project": {"select": {"name": entry.project.value}},
                "Status": {"select": {"name": entry.status.value}},
                "Source": {"select": {"name": entry.source.value}},
                "Pinned": {"checkbox": entry.pinned},
            }

            if entry.tags:
                properties["Tags"] = {
                    "multi_select": [{"name": tag} for tag in entry.tags]
                }

            blocks: List[dict] = []
            if entry.content:
                content_blocks = markdown_to_blocks(entry.content)
                for chunk in chunk_blocks(content_blocks):
                    blocks.extend(chunk)

            page = self.client.pages.create(
                parent={"database_id": settings.inbox_database_id},
                properties=properties,
                children=blocks,
            )

            return page["id"], page.get("url", "")

        except (NotionAuthError, NotionNotFoundError, NotionPermissionError):
            raise
        except Exception as e:
            _classify_notion_error(e, "Database")

    def append_to_daily_rollup(self, page_id: str, title: str, page_url: str) -> None:
        """Append an entry link to today's section of the daily rollup page.

        Raises:
            NotionAuthError, NotionNotFoundError, NotionPermissionError
        """
        if not settings.daily_rollup_page_id:
            return

        try:
            from datetime import date

            today = date.today().isoformat()
            heading_text = f"Inbox entries - {today}"

            existing_blocks = self.client.blocks.children.list(
                block_id=settings.daily_rollup_page_id
            )
            has_heading_today = any(
                block.get("type") == "heading_2"
                and block["heading_2"].get("rich_text")
                and len(block["heading_2"]["rich_text"]) > 0
                and block["heading_2"]["rich_text"][0].get("text", {}).get("content")
                == heading_text
                for block in existing_blocks.get("results", [])
            )

            blocks_to_add: List[dict] = []
            if not has_heading_today:
                blocks_to_add.append(_make_heading(2, heading_text))

            blocks_to_add.append(
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": title, "link": {"url": page_url}},
                            }
                        ]
                    },
                }
            )

            self.client.blocks.children.append(
                block_id=settings.daily_rollup_page_id, children=blocks_to_add
            )

        except (NotionAuthError, NotionNotFoundError, NotionPermissionError):
            raise
        except Exception as e:
            _classify_notion_error(e, "Daily rollup page")
