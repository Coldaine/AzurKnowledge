# Implementation Prompt for Azur Lane Equipment Database

Objective
- Implement the repository exactly as specified in `Architecture.md`, using JSON files + small Python scripts (no database), with polite scraping defaults and simple progress tracking in git.

Key Deliverables
- Repository structure and files under `azur-lane-equipment-db/` matching `Architecture.md`.
- Working scripts in `scripts/`: `utils.py`, `scraper.py`, `run_collection.py`.
- Seed data files in `data/equipment/` (empty arrays) for all canonical slugs.
- A valid `progress.json` file and `logs/` directory creation.
- `.gitignore`, `requirements.txt`, and a minimal `README.md` from the doc.

Repo Structure (must match)
- `data/equipment/`: create empty JSON arrays for each slug
  - `destroyer_guns.json`, `light_cruiser_guns.json`, `heavy_cruiser_guns.json`, `large_cruiser_guns.json`, `battleship_guns.json`, `anti_air_guns.json`, `ship_torpedoes.json`, `submarine_torpedoes.json`, `fighters.json`, `dive_bombers.json`, `torpedo_bombers.json`, `seaplanes.json`, `auxiliary_equipment.json`, `augment_modules.json`, `anti_submarine_equipment.json`
- `data/schema_example.json`: include the JSON schema example from `Architecture.md`.
- `data/raw/`: leave empty (used as temporary cache directory).
- `scripts/`: `utils.py`, `scraper.py`, `run_collection.py` (see implementation details).
- `logs/`: include empty directory; scripts must ensure it exists.
- `.gitignore`, `README.md`, `requirements.txt`, `progress.json`.

Implementation Details
- `scripts/utils.py`
  - Functions: `load_json(filepath)`, `save_json(data, filepath)`, `update_progress(item_name, status)`, `commit_changes(item_names, status)`.
  - Ensure directory creation for save paths; `save_json` should create parent dirs when needed.
  - `commit_changes` must stage `data/equipment` and `progress.json` (avoid shell globs), and commit only if there are staged changes. Include a concise message using up to 3 item names, then `(+N more)`.
- `scripts/scraper.py`
  - Use `requests.Session()` with a desktop UA; set `self.request_timeout = 10`, `self.delay_seconds = 1.0`.
  - Ensure `logs/` exists before configuring logging. Configure `logging` to write to `logs/scraping.log`.
  - Public methods: `scrape_item(item_name, equipment_type_slug)`, `scrape_wiki(item_name)`, `scrape_community_guides(item_name)`, `save_item(item_data, equipment_type_slug)`.
  - `scrape_item` must set `identity.type` to the canonical slug (e.g., `destroyer_guns`) and merge dict fields from source methods. Prefer tracking source URLs in `metadata.sources` when available.
  - `save_item` writes into `data/equipment/{equipment_type_slug}.json`, replaces an entry by `identity.itemName` if found, and calls `update_progress` with `basic|partial|complete` based on collected fields.
  - Include a small example block under `if __name__ == "__main__":` scraping one item and committing.
- `scripts/run_collection.py`
  - Iterate a small list of `(item_name, equipment_type_slug)` pairs, call `scrape_item` then `save_item`, commit every 5 items, and commit any remainder at the end.
- `progress.json`
  - Initialize with: `{ "completed": [], "partial": [], "failed": [], "retry_queue": [], "last_updated": "" }` (no extra statistics unless `utils.update_progress` maintains them).
- `.gitignore`, `requirements.txt`, `README.md`
  - Copy contents from `Architecture.md`. `requirements.txt` includes: `requests`, `beautifulsoup4`, `lxml` exact versions listed.

Constraints
- Do not add a database or new dependencies beyond those listed.
- Keep `identity.type` equal to the file slug (e.g., `destroyer_guns`). Be consistent across code and data.
- Be polite with network usage: use timeouts and `time.sleep(self.delay_seconds)` between requests in scraping methods.
- Keep code minimal; leave `scrape_wiki`/`scrape_community_guides` as placeholders returning `{}` unless specified otherwise in comments.

Acceptance Criteria
- Running `python scripts/scraper.py` creates `logs/`, updates one equipment JSON file, updates `progress.json`, and makes a git commit if there are changes.
- Running `python scripts/run_collection.py` processes the list, batching commits every 5 items.
- All listed files exist with correct names and basic contents. `data/equipment/*.json` files exist and contain `[]` initially.
- No wildcard import usage; imports are explicit and paths resolve when run from repo root.

How to Proceed (step-by-step)
1) Scaffold directories and empty JSON files per the structure above.
2) Create `.gitignore`, `requirements.txt`, and `README.md` from `Architecture.md` contents.
3) Implement `scripts/utils.py` with robust staging/commit behavior and JSON helpers.
4) Implement `scripts/scraper.py` with logging setup, polite defaults, and example usage.
5) Implement `scripts/run_collection.py` per the batching example.
6) Sanity test locally: run the two scripts, verify file updates and a commit is created when content changes.
7) Stop. Do not overengineer beyond `Architecture.md`.

Notes
- License and robots: respect the Azur Lane Wiki CC BY-NC-SA license and robots.txt guidance; add a short “Sources/Credits” note in `README.md` when publishing scraped data.
