# Rebuilding

Install ReportLab and python-chess in your Python environment, then run `python build_collection.py --output <new-output-directory>` from this directory. The builder reads the retained data and does not need network access. On Windows it uses `C:/Windows/Fonts/seguisym.ttf` for chess glyphs; adapt `FONT` to an installed font containing U+2654-U+265F on other systems, respecting that font's embedding license. Engine binaries and package installations are not part of the repository.

`core_lessons.py` contains 120 original concept lessons. `themes.py` contains 36 original theme explanations. `puzzles.json` contains the 2,880 selected CC0 records. `engine-audit.json` records the automated root-position checks. The builder annotates legal board changes and computes checkpoints, rather than inserting arbitrary move strings into prose.

Rebuilding generates the course, indexes, and sources. Run your own validation afterward before replacing a published collection. The delivered `QUALITY.md` describes the checks made for the published edition.
