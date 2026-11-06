"""
pick.py
-------
Two-level Random Generator & List Printer from the shell:
1. Level 1 (Home / Undecided):
       python pick.py
   Randomly picks a section that has active items, then picks a random item from it!
2. Level 2 (Specific Section):
       python pick.py movie
   Randomly picks an uncompleted item from that section only.
3. Print full list:
       python pick.py list
       python pick.py list movie
"""

import random
import sys
from list_utils import SECTION_NAMES, SECTIONS_DIR, pick_section, parse_items


def get_active_items(section):
    path = SECTIONS_DIR / f"{section}.html"
    if not path.exists():
        return []
    items = parse_items(path.read_text(encoding="utf-8"))
    return [it for it in items if not it["done"]]


def print_lists(target_section=None):
    sections = [target_section] if target_section else SECTION_NAMES
    for sec in sections:
        path = SECTIONS_DIR / f"{sec}.html"
        if not path.exists():
            continue
        items = parse_items(path.read_text(encoding="utf-8"))
        active = [it for it in items if not it["done"]]
        done = [it for it in items if it["done"]]
        print(f"\n=== {sec.upper()} ({len(active)} active, {len(done)} done) ===")
        if not items:
            print("  (empty)")
            continue
        for i, it in enumerate(items, 1):
            mark = "✓" if it["done"] else "•"
            tag = f" [{it['tag']}]" if it["tag"] else ""
            print(f"  {mark} {it['title']}{tag}")


def main():
    arg1 = sys.argv[1].strip().lower() if len(sys.argv) > 1 else None
    arg2 = sys.argv[2].strip().lower() if len(sys.argv) > 2 else None

    if arg1 == "list":
        if arg2:
            sec, _ = pick_section(arg2)
            if sec:
                print_lists(sec)
        else:
            print_lists()
        return

    # Level 1: No section specified -> Pick section first, then pick item
    if not arg1:
        available_sections = {}
        for sec in SECTION_NAMES:
            active = get_active_items(sec)
            if active:
                available_sections[sec] = active

        if not available_sections:
            print("\nNo active items left in any section! Add some with: python add.py")
            return

        chosen_sec = random.choice(list(available_sections.keys()))
        chosen_item = random.choice(available_sections[chosen_sec])
        tag_str = f" [{chosen_item['tag']}]" if chosen_item["tag"] else ""

        print("\n🎲 LEVEL 1 RANDOM PICK (Across All Sections)")
        print("---------------------------------------------")
        print(f"👉 Category Chosen : {chosen_sec.upper()}")
        print(f"🎬 Selected Item   : {chosen_item['title']}{tag_str}")
        if chosen_item["note"] and chosen_item["note"] != "No notes yet.":
            print(f"📝 Note            : {chosen_item['note']}")
        print("---------------------------------------------\n")
        return

    # Level 2: Specific section specified -> Pick inside that section
    sec, _ = pick_section(arg1)
    if not sec:
        return
    active = get_active_items(sec)
    if not active:
        print(f"\nNo active items left in {sec.upper()}! Everything is done or empty.")
        return

    chosen_item = random.choice(active)
    tag_str = f" [{chosen_item['tag']}]" if chosen_item["tag"] else ""
    print(f"\n🎲 LEVEL 2 RANDOM PICK ({sec.upper()} ONLY)")
    print("---------------------------------------------")
    print(f"🎬 Selected {sec.capitalize()} : {chosen_item['title']}{tag_str}")
    if chosen_item["note"] and chosen_item["note"] != "No notes yet.":
        print(f"📝 Note            : {chosen_item['note']}")
    print("---------------------------------------------\n")


if __name__ == "__main__":
    main()
