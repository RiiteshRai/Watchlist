"""
status.py
---------
Mark an item as DONE, Delete it, or Edit its note from the shell
(works just like logic.py in CF_QUES_LIST).
Usage:
    python status.py movie
    python status.py anime
"""

import sys
import re
from html import escape
from list_utils import pick_section, parse_items


def main():
    section, file = pick_section(sys.argv[1] if len(sys.argv) > 1 else None)
    if not file:
        return

    html = file.read_text(encoding="utf-8")
    items = parse_items(html)

    if not items:
        print(f"No items found in {section}.")
        return

    print(f"\n=== {section.upper()} LIST ===\n")
    for i, item in enumerate(items, 1):
        mark = "✓ DONE" if item["done"] else "  TODO"
        tag_str = f" [{item['tag']}]" if item["tag"] else ""
        print(f"{i}. [{mark}] {item['title']}{tag_str}")

    search = input("\nChoose item number or type part of the title: ").strip()
    if not search:
        return

    selected = None
    if search.isdigit() and 1 <= int(search) <= len(items):
        selected = items[int(search) - 1]
    else:
        needle = search.lower()
        matches = [it for it in items if needle in it["title"].lower()]
        if len(matches) == 1:
            selected = matches[0]
        elif len(matches) > 1:
            print("\nMultiple matches:")
            for i, it in enumerate(matches, 1):
                print(f"{i}. {it['title']}")
            n = input("Choose number: ").strip()
            if n.isdigit() and 1 <= int(n) <= len(matches):
                selected = matches[int(n) - 1]

    if not selected:
        print("Item not found.")
        return

    print(f"\nSelected: {selected['title']}")
    print("  1. Mark as DONE (won't be picked by random generator)")
    print("  2. Mark as TO WATCH / TODO (put back in active rotation)")
    print("  3. Update note / thoughts")
    print("  4. DELETE permanently from list")
    choice = input("Choose 1/2/3/4: ").strip()

    original = selected["block"]

    if choice == "4":
        html = html.replace(original + "\n", "", 1)
        if original in html:
            html = html.replace(original, "", 1)
        file.write_text(html, encoding="utf-8")
        print(f"\n✓ Deleted '{selected['title']}' from {section}.")
        return

    new_block = original
    if choice == "3":
        note = input("Enter new note: ").strip() or "No notes yet."
        new_block = re.sub(r"<p>.*?</p>", f"<p>{escape(note)}</p>", new_block, count=1, flags=re.S)
        print("\n✓ Note updated!")
    elif choice == "1":
        new_block = re.sub(r'class="question[^"]*"', 'class="question solved"', new_block, count=1)
        new_block = re.sub(r'data-status="[^"]*"', 'data-status="done"', new_block, count=1)
        new_block = re.sub(r'<input type="checkbox"[^>]*>', '<input type="checkbox" checked>', new_block, count=1)
        new_block = re.sub(r'<span class="status">.*?</span>', '<span class="status">DONE</span>', new_block, count=1)
        print(f"\n✓ Marked '{selected['title']}' as DONE!")
    elif choice == "2":
        new_block = re.sub(r'class="question[^"]*"', 'class="question"', new_block, count=1)
        new_block = re.sub(r'data-status="[^"]*"', 'data-status="todo"', new_block, count=1)
        new_block = re.sub(r'<input type="checkbox"[^>]*>', '<input type="checkbox">', new_block, count=1)
        new_block = re.sub(r'<span class="status">.*?</span>', '<span class="status">TO WATCH / READ</span>', new_block, count=1)
        print(f"\n✓ Marked '{selected['title']}' as TODO!")
    else:
        print("No changes made.")
        return

    html = html.replace(original, new_block, 1)
    file.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
