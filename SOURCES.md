# Sources and methods

The prose concept lessons and thematic teaching notes were written for Chess Keys with AI assistance. They are educational summaries and practical examples, not copied pages from chess books. This collection has automated chess and document checks, plus sampled visual review; it has not received a full human chess-editor review of every page.

## Practice data

The 2,880 practice positions and recorded solution lines come from the [Lichess open puzzle database](https://database.lichess.org/#puzzles), whose database exports are dedicated to the public domain under [CC0](https://creativecommons.org/publicdomain/zero/1.0/). The database page identified the source snapshot as 2026-09-10 when retrieved for this build on 2026-09-29 UTC. Each practice PDF links to its specific puzzle; `source/puzzles.json` retains puzzle ID, original FEN, source move sequence, rating, themes, and game URL.

The first move in a Lichess puzzle row is the opponent's setup move. This build applies it before drawing the diagram. The solution begins with the second source move. White is always at the bottom of the diagrams, even when Black moves next. Gold square borders identify the setup move. No position is duplicated in the practice set, including positions with different move counters.

Selection uses source puzzle ratings 650-2400, popularity at least 80, at least 100 recorded plays, and source sequences of at most ten plies including setup. Each of 36 theme chapters contains 80 unique positions, ordered by source rating. One position can have several themes; it is assigned to exactly one chapter.

## Chess checks and interpretation

All starting boards are checked for structural validity with python-chess. Every setup and solution move is replayed and checked for legality. All source lines tagged mate are required to finish in actual checkmate. Material checkpoints are computed from the board using P=1, N/B=3, R=5, Q=9; these are teaching approximations rather than a complete evaluation.

Stockfish 19 performed a 30,000-node MultiPV 2 comparison at each exercise's initial position, with an additional 30,000-node source-move search when needed. A large apparent disagreement triggered a deeper 3,000,000-node MultiPV 3 review. The one flagged case was resolved: the source move forces mate. This is an automated sanity check, not exhaustive proof of every defensive branch. The full audit is retained in `source/engine-audit.json`.

The displayed continuation is a recorded solution branch. A statement such as 'three legal replies' is a legal-move count, not a claim that all three are equally strong. Geometric attacks or undefended pieces may have tactical qualifications; the prose explicitly asks the reader to check them. Theoretical endgame guidance is conditional on the described arrangement rather than a universal promise of a win.

## References and tools

- [FIDE Laws of Chess](https://handbook.fide.com/chapter/E012023): reference for standard-chess rules, not a substitute for local tournament regulations.
- [Lichess database documentation](https://database.lichess.org/#puzzles): data license, schema, and setup-move convention.
- [python-chess](https://python-chess.readthedocs.io/): board validity, move legality, SAN, and mate detection.
- [Stockfish](https://stockfishchess.org/): engine review. Engine binaries are not included in this repository.
- ReportLab generated the PDFs; Poppler and PyMuPDF were used for rendering and inspection. Chess glyphs are embedded from the system's Segoe UI Symbol font; the font file itself is not distributed.

No separate reuse license has been assigned to the original instructional text or build code. The Lichess records retain their CC0 status. Third-party software and fonts retain their own licenses; their packages are not redistributed here.
