"""
list_utils.py
-------------
Shared helpers for add.py, status.py, and pick.py:
- SECTIONS_DIR and SECTION_NAMES
- pick_section(arg) -> select section by name or prompt
- parse_items(html) -> extract all items from a section HTML file
"""

import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SECTIONS_DIR = ROOT / "sections"
SECTION_NAMES = ["movie", "series", "anime", "book", "project"]

ALIASES = {
    "movies": "movie",
    "show": "series",
    "shows": "series",
    "animes": "anime",
    "books": "book",
    "projects": "project",
}


def pick_section(arg=None):
    """Returns (name, path) for a section page, or (None, None) if invalid."""
    raw = (arg or input(f"Section ({' / '.join(SECTION_NAMES)}): ")).strip().lower()
    if raw.endswith(".html"):
        raw = raw[:-5]
    raw = ALIASES.get(raw, raw)
    if raw not in SECTION_NAMES:
        print(f"Error: section must be one of: {', '.join(SECTION_NAMES)}.")
        return None, None
    path = SECTIONS_DIR / f"{raw}.html"
    if not path.exists():
        print(f"Error: {path} does not exist.")
        return None, None
    return raw, path


def parse_items(html):
    """Returns list of dicts for each <div class="question"...> block in html."""
    blocks = re.findall(r'<div class="question[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>|<div class="question[^"]*"[^>]*>.*?</div>', html, re.S)
    # Using explicit marker split for clean block extraction
    items = []
    pattern = re.compile(
        r'(<div class="question([^"]*)"\s+data-status="([^"]*)"[^>]*>\s*'
        r'<div class="question-header">\s*<div class="question-left">\s*'
        r'<input type="checkbox"[^>]*>\s*'
        r'<span class="item-title">(.*?)</span>'
        r'(?:\s*<span class="tag">(.*?)</span>)?'
        r'.*?</div>\s*</div>\s*'
        r'<p>(.*?)</p>\s*'
        r'<span class="status">(.*?)</span>\s*</div>)',
        re.S
    )
    for m in pattern.finditer(html):
        full_block = m.group(1)
        classes = m.group(2)
        status_attr = m.group(3)
        title = unescape(m.group(4).strip())
        tag = unescape(m.group(5).strip()) if m.group(5) else ""
        note = unescape(m.group(6).strip())
        status_text = unescape(m.group(7).strip())
        is_done = (status_attr == "done") or ("solved" in classes)
        items.append({
            "title": title,
            "tag": tag,
            "note": note,
            "done": is_done,
            "status": status_text,
            "block": full_block,
        })
    return items
