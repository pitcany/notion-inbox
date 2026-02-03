#!/usr/bin/env python3
import argparse
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()


def read_stdin():
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return None


def call_api(entry: dict, api_url: str = "http://127.0.0.1:8787/v1/inbox"):
    import requests

    try:
        response = requests.post(api_url, json=entry, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "Could not connect to API server. Is it running?"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": f"Request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"ok": False, "error": "Invalid response from server"}


def call_direct(entry: dict):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.models import InboxEntry
    from app.service import create_inbox_entry

    inbox_entry = InboxEntry(**entry)
    response = create_inbox_entry(inbox_entry)
    return response.model_dump()


def main():
    parser = argparse.ArgumentParser(description="Notion Inbox CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    inbox_parser = subparsers.add_parser("inbox", help="Create inbox entry")
    inbox_parser.add_argument("--title", required=True, help="Entry title")
    inbox_parser.add_argument("--content", help="Entry content (supports Markdown)")
    inbox_parser.add_argument(
        "--type",
        default="note",
        choices=["idea", "note", "meeting", "research", "task"],
        help="Entry type",
    )
    inbox_parser.add_argument(
        "--project",
        default="Personal",
        choices=["Steward", "Tutoring", "Quant", "Personal", "Work"],
        help="Project",
    )
    inbox_parser.add_argument(
        "--status",
        default="inbox",
        choices=["inbox", "triage", "next", "done"],
        help="Status",
    )
    inbox_parser.add_argument("--tags", help="Comma-separated tags")
    inbox_parser.add_argument(
        "--source",
        default="ChatGPT",
        choices=["ChatGPT", "manual", "voice", "web"],
        help="Source",
    )
    inbox_parser.add_argument("--pinned", action="store_true", help="Pin the entry")
    inbox_parser.add_argument(
        "--daily", action="store_true", help="Also add to daily rollup"
    )
    inbox_parser.add_argument(
        "--direct", action="store_true", help="Write directly to Notion (bypass API)"
    )
    inbox_parser.add_argument(
        "--api-url", default="http://127.0.0.1:8787", help="API base URL"
    )

    args = parser.parse_args()

    if args.command != "inbox":
        parser.print_help()
        return 1

    content = args.content or read_stdin()
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    entry = {
        "title": args.title,
        "content": content,
        "type": args.type,
        "project": args.project,
        "status": args.status,
        "tags": tags,
        "source": args.source,
        "pinned": args.pinned,
        "also_add_to_daily_rollup": args.daily,
    }

    api_url = f"{args.api_url.rstrip('/')}/v1/inbox"

    if args.direct:
        result = call_direct(entry)
    else:
        result = call_api(entry, api_url)

    if result.get("ok"):
        print(f"Created: {result.get('url')}")
        return 0
    else:
        print(f"Error: {result.get('error')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
