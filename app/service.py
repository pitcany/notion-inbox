from app.models import InboxEntry, InboxResponse
from app.notion_client import NotionClient
from app.exceptions import NotionInboxError


def create_inbox_entry(
    entry: InboxEntry, notion: NotionClient | None = None
) -> InboxResponse:
    """Orchestrate inbox page creation and optional daily rollup.

    This is the single source of truth for the create-entry flow,
    used by both the API endpoint and the CLI direct mode.
    """
    if notion is None:
        notion = NotionClient()

    try:
        page_id, page_url = notion.create_inbox_page(entry)

        if entry.also_add_to_daily_rollup and page_id and page_url:
            try:
                notion.append_to_daily_rollup(page_id, entry.title, page_url)
            except NotionInboxError as e:
                return InboxResponse(
                    ok=False,
                    error=f"Created page but failed to add to daily rollup: {e}",
                )

        return InboxResponse(ok=True, page_id=page_id, url=page_url)

    except NotionInboxError as e:
        return InboxResponse(ok=False, error=str(e))
    except Exception as e:
        return InboxResponse(ok=False, error=f"Unexpected error: {e}")
