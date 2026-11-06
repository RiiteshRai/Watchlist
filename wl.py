#!/usr/bin/env python3
"""
wl.py — Simple Terminal Watchlist (Exact CF_QUES_LIST Loop Style)
=================================================================
All items are stored in `watchlist.md` in the same folder.

COMMANDS (same on Laptop & Mobile):
  python wl.py add movie      -> Loop to add multiple items (type "done" to finish)
  python wl.py pick           -> Level 1 Random: picks random section, then random item
  python wl.py pick movie     -> Level 2 Random: picks random item from movie only
  python wl.py list           -> Print full list (or: python wl.py list movie)
  python wl.py done movie     -> Mark item as done / undone (by number or name)
  python wl.py del movie      -> Delete item (by number or name)
  python wl.py sync           -> Sync with your GitHub repo (pull + commit + push)
"""

import random
import re
import subprocess
import sys
from pathlib import Path

MD_FILE = Path(__file__).resolve().parent / "watchlist.md"
SECTIONS = ["movie", "series", "anime", "book", "project"]

ALIASES = {
    "movies": "movie",
    "show": "series", "shows": "series",
    "animes": "anime",
    "books": "book",
    "projects": "project",
}

STARTER_MD = """# My Watchlist & Projects

## Movie
- [ ] Memento
- [ ] Interstellar
- [x] Parasite

## Series
- [ ] Severance
- [ ] Dark

## Anime
- [ ] Frieren: Beyond Journey's End
- [ ] Steins;Gate

## Book
- [ ] Project Hail Mary
- [x] Atomic Habits

## Project
- [ ] Terminal Watchlist CLI
- [ ] Expense Tracker Script
"""


def pick_section(arg=None):
    raw = (arg or input(f"Section ({' / '.join(SECTIONS)}): ")).strip().lower()
    raw = ALIASES.get(raw, raw)
    if raw not in SECTIONS:
        print(f"Error: section must be one of: {', '.join(SECTIONS)}.")
        return None
    return raw


def load_data():
    if not MD_FILE.exists():
        MD_FILE.write_text(STARTER_MD, encoding="utf-8")

    data = {sec: [] for sec in SECTIONS}
    current_sec = None

    for line in MD_FILE.read_text(encoding="utf-8").splitlines():
        h = re.match(r"^##\s+(.+)$", line.strip())
        if h:
            sec = h.group(1).strip().lower()
            sec = ALIASES.get(sec, sec)
            if sec in SECTIONS:
                current_sec = sec
            continue

        if current_sec:
            m = re.match(r"^-\s*\[([ xX])\]\s+(.+)$", line.strip())
            if m:
                data[current_sec].append({
                    "title": m.group(2).strip(),
                    "done": m.group(1).lower() == "x",
                })
    return data


def save_data(data):
    lines = ["# My Watchlist & Projects", ""]
    for sec in SECTIONS:
        lines.append(f"## {sec.capitalize()}")
        for it in data[sec]:
            mark = "x" if it["done"] else " "
            lines.append(f"- [{mark}] {it['title']}")
        lines.append("")
    MD_FILE.write_text("\n".join(lines), encoding="utf-8")


def find_duplicate(data, title):
    needle = title.strip().lower()
    for sec in SECTIONS:
        for it in data[sec]:
            if it["title"].lower() == needle:
                return sec
    return None


def add_items(data, section):
    """Exact CF_QUES_LIST/add.py loop: keep adding until user types 'done'."""
    print(f"\nAdding items to {section}")
    print('Type the name. Type "done" when finished.\n')
    added = 0

    while True:
        title = input(f"{section.capitalize()} name: ").strip()
        if title.lower() == "done":
            break
        if not title:
            print("Name cannot be empty.\n")
            continue

        dup = find_duplicate(data, title)
        if dup:
            print(f"This item is already in '{dup}'. Skipped.\n")
            continue

        data[section].append({"title": title, "done": False})
        save_data(data)
        added += 1
        print(f"✓ Added: {title}\n")

    print(f"Done! Added {added} new item(s) to {section}.")


def pick_random(data, section=None):
    # Level 1: No section given -> Pick a random section first, then a random active item
    if not section:
        available = {
            s: [it for it in data[s] if not it["done"]]
            for s in SECTIONS
        }
        non_empty = [s for s, items in available.items() if items]
        if not non_empty:
            print("\nNo active items left in any section!")
            return

        chosen_sec = random.choice(non_empty)
        chosen_item = random.choice(available[chosen_sec])
        print(f"\n🎲 Random Section : {chosen_sec.upper()}")
        print(f"🎬 Random Pick    : {chosen_item['title']}\n")
        return

    # Level 2: Section given -> Pick from that section only
    active = [it for it in data[section] if not it["done"]]
    if not active:
        print(f"\nNo active items left in {section}!")
        return

    chosen_item = random.choice(active)
    print(f"\n🎲 Random {section.capitalize()} : {chosen_item['title']}\n")


def print_list(data, section=None):
    targets = [section] if section else SECTIONS
    for sec in targets:
        items = data[sec]
        active_count = sum(1 for it in items if not it["done"])
        print(f"\n=== {sec.upper()} ({active_count} active / {len(items)} total) ===")
        if not items:
            print("  (empty)")
            continue
        for i, it in enumerate(items, 1):
            status = "[x]" if it["done"] else "[ ]"
            print(f"  {i}. {status} {it['title']}")
    print()


def select_item(items, section):
    if not items:
        print(f"No items found in {section}.")
        return None

    print(f"\n=== {section.upper()} ===\n")
    for i, it in enumerate(items, 1):
        status = "[DONE]" if it["done"] else "[TODO]"
        print(f"{i}. {status} {it['title']}")

    search = input("\nChoose number or name: ").strip()
    if not search:
        return None

    if search.isdigit() and 1 <= int(search) <= len(items):
        return int(search) - 1

    needle = search.lower()
    matches = [idx for idx, it in enumerate(items) if needle in it["title"].lower()]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print("\nMultiple matches:")
        for k, idx in enumerate(matches, 1):
            print(f"{k}. {items[idx]['title']}")
        n = input("Choose number: ").strip()
        if n.isdigit() and 1 <= int(n) <= len(matches):
            return matches[int(n) - 1]

    print("Item not found.")
    return None


def update_status(data, section, mode="done"):
    items = data[section]
    idx = select_item(items, section)
    if idx is None:
        return

    if mode == "del":
        removed = items.pop(idx)
        save_data(data)
        print(f"\n✓ Deleted: {removed['title']}")
        return

    item = items[idx]
    print(f"\nSelected: {item['title']}")
    print("  1. Done (won't come again in random pick)")
    print("  2. Not done yet (keep in list)")
    choice = input("Choose 1/2 (or press Enter to toggle): ").strip()

    if choice == "1":
        item["done"] = True
    elif choice == "2":
        item["done"] = False
    else:
        item["done"] = not item["done"]

    save_data(data)
    state = "DONE" if item["done"] else "NOT DONE"
    print(f"\n✓ Updated '{item['title']}' -> {state}!")


def sync_git():
    print("================================")
    print("     WATCHLIST TRACKER SYNC     ")
    print("================================")
    subprocess.run("git pull --rebase --autostash", shell=True)
    subprocess.run("git add watchlist.md wl.py", shell=True)
    res = subprocess.run('git commit -m "Update watchlist"', shell=True)
    if res.returncode == 0:
        subprocess.run("git push", shell=True)
        print("\n✓ Your watchlist has been synced!")
    else:
        print("\n✓ Already up to date (nothing new to commit).")


def main():
    data = load_data()
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    if cmd == "add":
        sec = pick_section(arg)
        if sec:
            add_items(data, sec)

    elif cmd == "pick":
        sec = pick_section(arg) if arg else None
        if arg and not sec:
            return
        pick_random(data, sec)

    elif cmd == "list":
        sec = pick_section(arg) if arg else None
        if arg and not sec:
            return
        print_list(data, sec)

    elif cmd == "done":
        sec = pick_section(arg)
        if sec:
            update_status(data, sec, mode="done")

    elif cmd in ("del", "delete"):
        sec = pick_section(arg)
        if sec:
            update_status(data, sec, mode="del")

    elif cmd == "sync":
        sync_git()

    else:
        print(__doc__)


if __name__ == "__main__":
    main()