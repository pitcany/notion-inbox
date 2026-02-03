class NotionInboxError(Exception):
    """Base exception for Notion Inbox operations."""


class NotionAuthError(NotionInboxError):
    """Raised when the Notion token is invalid or revoked."""

    def __init__(
        self, message: str = "Invalid NOTION_TOKEN or integration not authorized"
    ):
        super().__init__(message)


class NotionNotFoundError(NotionInboxError):
    """Raised when a database or page is not found or not shared."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found or not shared with integration")


class NotionPermissionError(NotionInboxError):
    """Raised when the integration lacks permission."""

    def __init__(self, resource: str = "resource"):
        super().__init__(f"Integration does not have permission to access {resource}")
