"""
add.py
------
Add items to any section from the shell (just like CF_QUES_LIST/add.py).
Usage:
    python add.py movie
    python add.py anime
    python add.py
"""

import sys
from html import escape
from list_utils import pick_section, parse_items, SECTIONS_DIR


def find_duplicate(title):
    """Checks all sections so the same title isn't added twice."""
    needle = title.strip().lower()
    for f in sorted(SECTIONS_DIR.glob("*.html")):
        for item in parse_items(f.read_text(encoding="utf-8")):
            if item["title"].lower() == needle:
                return f.stem
    return None


def insert_block(html, block):
    marker = "<!-- ITEMS_END -->"
    pos = html.find(marker)
    if pos == -1:
        return None
    return html[:pos] + block + "\n" + html[pos:]


def add_items(section, file):
    print(f"\nAdding items to {section.upper()}")
    print('Type the title (e.g. "Memento"). Type "done" when finished.\n')
    added = 0

    while True:
        title = input(f"{section.capitalize()} title: ").strip()
        if title.lower() == "done":
            break
        if not title:
            print("Title cannot be empty.\n")
            continue

        dup = find_duplicate(title)
        if dup:
            print(f"'{title}' is already in '{dup}'. Skipped.\n")
            continue

        tag = input("   Tag / Genre / Mood (optional, press Enter to skip): ").strip()
        note = input("   Short note (optional, press Enter to skip): ").strip()

        tag_html = f' <span class="tag">{escape(tag)}</span>' if tag else ""
        note_text = escape(note) if note else "No notes yet."

        block = (
            '<div class="question" data-status="todo">\n'
            '<div class="question-header">\n'
            '<div class="question-left">\n'
            '<input type="checkbox">\n'
            f'<span class="item-title">{escape(title)}</span>{tag_html}\n'
            '</div>\n'
            '</div>\n'
            f'<p>{note_text}</p>\n'
            '<span class="status">TO WATCH / READ</span>\n'
            '</div>\n'
        )

        html = file.read_text(encoding="utf-8")
        new_html = insert_block(html, block)
        if new_html is None:
            print("Error: Could not find <!-- ITEMS_END --> marker in section file.")
            return
        file.write_text(new_html, encoding="utf-8")
        added += 1
        print(f"✓ Added: {title}\n")

    print(f"Done! Added {added} new item(s) to {section}.")


def main():
    section, file = pick_section(sys.argv[1] if len(sys.argv) > 1 else None)
    if not file:
        return
    add_items(section, file)


if __name__ == "__main__":
    main()
