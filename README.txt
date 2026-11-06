WATCHLIST & PROJECT TRACKER (Movie / Series / Anime / Book / Project)
======================================================================
Built in the exact style of your CF_QUES_LIST project!

1. HOW IT WORKS ON YOUR MOBILE (GitHub Pages):
   - Home Page (index.html):
     * Has the LEVEL 1 Random Generator ("🎲 Not sure? Surprise me from ANY section").
       It picks a category first (e.g. Movie vs Series vs Anime) and then picks an active item!
     * Shows all 5 section cards (Movies, Series, Anime, Books, Projects).
   - Inside Each Section (sections/movie.html, series.html, etc.):
     * Has the LEVEL 2 Random Generator ("🎲 Pick a random Movie") at the top of that section.
     * Shows the full clean list so you can just read/print it without rolling the dice.
     * Lets you add new items, check off items as DONE (so they never get picked again), or delete items right on your phone!

2. HOW IT WORKS IN THE SHELL (Laptop CLI):
   - ADD ITEMS:
       python add.py movie
       python add.py anime
     (Just type the name—no URLs needed! Type "done" when finished.)

   - PICK RANDOM FROM SHELL:
       python pick.py          -> Level 1: picks random section + random item
       python pick.py movie    -> Level 2: picks random item from Movie section
       python pick.py list     -> Prints your entire active list in the terminal

   - MARK DONE / DELETE / UPDATE NOTE:
       python status.py movie

   - PUSH TO GITHUB PAGES:
       python sync.py
