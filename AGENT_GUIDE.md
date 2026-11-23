\# AGENT\_GUIDE.md — Saudi Coffee Shop Guide (Advanced Programming 462)



\## 1. Project Overview \& Non-Negotiable Architecture

Build an individual Client-Server desktop application in Python for the \*\*Advanced Programming 462\*\* course:

\- \*\*Topic:\*\* Saudi Coffee Shop Guide (English only)

\- \*\*Extra Feature:\*\* \*\*Late-Night \& Vibe Spot Finder ("Find My Spot Now")\*\* — lets Saudi customers instantly find matching cafes based on late-night opening (past midnight / 24h), seating vibe, and coffee style.

\- \*\*Strict Architecture:\*\* `Tkinter GUI` <-> `Flask HTTP/JSON Server (port 5050)` <-> `SQLite Database`

\- \*\*Hard Rules:\*\*

&#x20; 1. All database access (`sqlite3`) MUST live strictly on the Flask back end (`shop\_store.py` called by `server.py`). Tkinter MUST NEVER import `sqlite3` or touch the `.db` file directly.

&#x20; 2. Users ONLY interact with the Tkinter GUI. Tkinter connects automatically to `http://127.0.0.1:5050`. Users never type server URLs or manually send requests.

&#x20; 3. Use ONLY Python standard library modules (`tkinter`, `tkinter.ttk`, `tkinter.messagebox`, `sqlite3`, `urllib.request`, `urllib.parse`, `urllib.error`, `json`, `socket`, `threading`) plus \*\*Flask\*\* (the only pip package).

&#x20; 4. Do NOT build HTML/JS front ends or use third-party HTTP libraries like `requests` or ORMs like SQLAlchemy.



\---



\## 2. Course Syllabus \& Coding Style Rules (Dr. Majed Hariri Style)

Because the student must explain every core line and perform a live small edit in a mandatory 3-minute oral check, follow these rules strictly:

1\. \*\*Extra-Simple, Flat, Readable Code:\*\* Avoid clever one-liners, nested comprehensions, decorators beyond `@app.route`, or over-engineered design patterns. Keep functions short, linear, and crystal clear.

2\. \*\*Block-Based Structure \& Comment Style:\*\*

&#x20;  - Group related lines into logical blocks separated by a single blank line.

&#x20;  - Start every block with a short, plain \*\*lowercase `# comment`\*\* naming what the block does (e.g., `# the application object`, `# read the fields from the body`, `# send the POST request`).

&#x20;  - Inside every function, method, and loop, place a short lowercase `# comment` above each logical step, indented to match the code.

&#x20;  - Do NOT write long multi-line docstrings or heavy type annotations.

3\. \*\*Database Style (`sqlite3`):\*\*

&#x20;  - Use one data access class (`ShopStore`) modeled on a clean store class: `\_\_init\_\_(self, db\_path)` opens `sqlite3.connect(db\_path)` and runs `CREATE TABLE IF NOT EXISTS ...`, plus methods for CRUD and `close()`.

&#x20;  - Always use `?` SQL placeholders and tuples `(val1, val2)` — NEVER f-strings or string concatenation in SQL.

&#x20;  - Use `with self.conn:` for write transactions (`INSERT`, `UPDATE`, `DELETE`) so changes commit automatically or roll back on error.

&#x20;  - In Flask, create a \*\*fresh `ShopStore(DB\_PATH)` per request\*\* and always close it in a `finally:` block.

4\. \*\*HTTP Client Style (`urllib`):\*\*

&#x20;  - Use `urlopen(url, timeout=5)` for `GET`.

&#x20;  - Use `urlencode(values).encode('utf-8')` passed as `data=` to `urlopen(url, data=body, timeout=5)` for `POST`. Flask reads fields with `request.form`.

&#x20;  - Parse replies with `json.loads(reply.read().decode('utf-8'))`.

&#x20;  - Catch exceptions in this exact order:

&#x20;    1. `except HTTPError as error:` (read and parse Flask's JSON error message from `error.read().decode('utf-8')`)

&#x20;    2. `except socket.timeout:`

&#x20;    3. `except URLError:`

5\. \*\*GUI Style (`tkinter`):\*\*

&#x20;  - Use `grid()` for widget placement (`padx`, `pady`) inside a clean main window class (`CoffeeGuideWindow(tk.Tk)`).

&#x20;  - Use `ttk.Treeview(..., show='headings')` for the coffee shop table.

&#x20;  - Use `messagebox.askyesno` to confirm deletion, and clear status labels / message boxes for success and error feedback.

&#x20;  - Put `if \_\_name\_\_ == '\_\_main\_\_':` guards on every executable file.

6\. \*\*Threading \& File Style (`report\_helper.py`):\*\*

&#x20;  - Use `threading.Thread(target=..., args=(...,))`, call `.start()`, and wait with `.join()` before printing the final status.

&#x20;  - Write the report using `with open(output\_path, 'w', encoding='utf-8') as report\_file:` and catch `OSError`.



\---



\## 3. Standard Project Structure \& Naming Conventions

Use clear, descriptive names so every variable, function, class, route, and widget is immediately recognizable:



\- `shop\_store.py` — Class `ShopStore` (SQLite table creation, CRUD, filtering, Find My Spot Now query, sample seeding).

\- `setup\_db.py` — Standalone script that creates the table (`IF NOT EXISTS`) and optionally seeds 6 sample Saudi coffee shops only if the table is empty (never deletes existing user records).

\- `server.py` — Flask app on `127.0.0.1:5050` with JSON API routes:

&#x20; - `GET /shops` — returns all shops (supports optional query params `region` and `min\_rating`). Also serves as the JSON route used by `report\_helper.py`.

&#x20; - `GET /shops/find\_spot` — extra feature ("Find My Spot Now") filtering by `open\_late`, `seating\_vibe`, and `coffee\_style`.

&#x20; - `POST /shops/add` — validates input (`400` on error), adds a shop, returns `200` + saved record.

&#x20; - `POST /shops/edit` — validates input (`400`) and ID existence (`404` if unknown), updates only that shop.

&#x20; - `POST /shops/delete` — validates ID (`400`/`404` if unknown), deletes only that shop.

\- `gui\_app.py` — Tkinter desktop app (`CoffeeGuideWindow(tk.Tk)`):

&#x20; - Widget names end with type suffixes: `name\_entry`, `region\_combo`, `rating\_entry`, `style\_combo`, `vibe\_combo`, `open\_late\_combo`, `notes\_entry`, `shops\_table`, `status\_label`, `add\_button`, `edit\_button`, `delete\_button`, `find\_spot\_button`.

&#x20; - Helper function `send\_request(path, form\_data=None)` handles all HTTP calls + error decoding in one place.

\- `report\_helper.py` — Terminal script that fetches `GET /shops`, spawns one `Thread` to write UTF-8 `coffee\_shops\_report.txt`, calls `join()`, and prints success/failure.

\- `tests/test\_store.py` and `tests/test\_api.py` — Automated verification scripts for Phases 1 \& 2.

\- `requirements.txt` — Lists `Flask`.

\- `README.md` — Full documentation, setup commands, Course Topic Evidence Table, test results, and AI assistance credit.

\- `CODE\_TRACE\_CHEATSHEET.md` — 3-minute oral defense trace \& live-edit drill guide.

\- `SLIDES\_OUTLINE.md` — 10-minute presentation outline.

\- `PROGRESS\_HANDOFF.md` — Agent state tracker updated after every phase.



\---



\## 4. Database Schema \& Sample Saudi Data

Table name: `coffee\_shops`

Columns:

\- `id` — `INTEGER PRIMARY KEY`

\- `name` — `TEXT NOT NULL` (required, non-empty)

\- `region` — `TEXT NOT NULL` (required, e.g., Riyadh, Jeddah, Madinah, Eastern Province, AlUla, Asir)

\- `rating` — `INTEGER NOT NULL` (required integer from `1` to `5`)

\- `coffee\_style` — `TEXT NOT NULL` (one of: `Saudi Qahwa`, `V60 / Specialty`, `Espresso \& Dessert`)

\- `seating\_vibe` — `TEXT NOT NULL` (one of: `Quiet Study`, `Social Hangout`, `Family Seating`, `Drive-Thru`)

\- `open\_late` — `TEXT NOT NULL` (`Yes` or `No`)

\- `notes` — `TEXT` (optional, defaults to `""`)



Default 6 Sample Saudi Coffee Shops (for `setup\_db.py`, inserted ONLY if table has 0 rows):

1\. `Elixir Bunn Coffee Roasters` | `Riyadh` | `5` | `V60 / Specialty` | `Quiet Study` | `Yes` | `Single-origin pour-over, calm seating for studying`

2\. `Brew92` | `Jeddah` | `5` | `V60 / Specialty` | `Social Hangout` | `Yes` | `Specialty roastery with lively late-night vibe`

3\. `Quba Heritage Qahwa` | `Madinah` | `5` | `Saudi Qahwa` | `Family Seating` | `Yes` | `Traditional cardamom qahwa and Ajwa dates`

4\. `Black Knight Coffee` | `Eastern Province` | `4` | `Espresso \& Dessert` | `Social Hangout` | `Yes` | `Popular Spanish latte and cheesecake in Khobar`

5\. `Maraya Desert Brew` | `AlUla` | `4` | `Saudi Qahwa` | `Family Seating` | `No` | `Scenic sunset seating with local roast`

6\. `Abha Mist Roasters` | `Asir` | `4` | `Espresso \& Dessert` | `Drive-Thru` | `No` | `Quick morning espresso stop in cool weather`



\---



\## 5. Phased Execution Plan (STOP AND TEST AFTER EVERY PHASE)

Work \*\*ONE phase at a time\*\*. Never skip testing. After every phase:

1\. Run verification tests and report exact output.

2\. Update `PROGRESS\_HANDOFF.md`.

3\. Remind the user to make a Git commit and wait for confirmation before starting the next phase.



\### Phase 1: Project Setup \& SQLite Data Layer

\- Create `.gitignore` (ignore `.venv/`, `\_\_pycache\_\_/`, `\*.pyc`, `coffee\_shops\_report.txt`), `requirements.txt` (`Flask`), `shop\_store.py`, `setup\_db.py`, and `tests/test\_store.py`.

\- Implement `ShopStore` with `create\_table`, `add\_shop`, `get\_all\_shops`, `get\_shop\_by\_id`, `update\_shop`, `delete\_shop`, `filter\_shops`, `find\_spot\_now`, `seed\_sample\_shops`, and `close`.

\- \*\*Mandatory Tests:\*\* Run `setup\_db.py` twice (verify idempotency and 6 rows preserved), then run `tests/test\_store.py` on a temporary test DB testing add, read, edit, delete, unknown ID (`None`/`0`), region/rating filter, and Find My Spot Now filter.



\### Phase 2: Flask Back-End API (`server.py`)

\- Create `server.py` running on `127.0.0.1:5050`.

\- Implement helper `validate\_shop\_form(form)` checking required fields, integer rating `1..5`, allowed `coffee\_style`, `seating\_vibe`, and `open\_late` values.

\- Implement routes: `GET /shops`, `GET /shops/find\_spot`, `POST /shops/add`, `POST /shops/edit`, `POST /shops/delete`.

\- Return JSON dictionaries on all routes: `200` on success, `400` on missing/invalid input, `404` on unknown ID, `500` JSON on unexpected DB error.

\- \*\*Mandatory Tests:\*\* Write and run `tests/test\_api.py` (using `urllib.request`, starting/targeting `server.py` on port 5050 or Flask test client + live port check) verifying:

&#x20; - `GET /shops` returns list

&#x20; - `POST /shops/add` valid (200), missing name (400), non-numeric rating (400), rating out of 1–5 range (400)

&#x20; - `POST /shops/edit` valid (200) and unknown ID `99999` (404)

&#x20; - `POST /shops/delete` valid (200) and unknown ID `99999` (404)

&#x20; - `GET /shops/find\_spot` returns matching late-night/vibe shops and handles empty result cleanly.



\### Phase 3: Tkinter Core CRUD \& Error Handling (`gui\_app.py`)

\- Create `gui\_app.py` with `CoffeeGuideWindow(tk.Tk)`.

\- Layout sections cleanly with `grid()`:

&#x20; 1. Form panel (Name, Region dropdown, Rating 1–5, Coffee Style dropdown, Seating Vibe dropdown, Open Late dropdown, Notes).

&#x20; 2. Action buttons (`Add Shop`, `Update Selected`, `Delete Selected`, `Clear Form`, `Refresh List`).

&#x20; 3. Filter bar (Region filter, Min Rating filter, `Apply Filter`, `Show All`).

&#x20; 4. Table (`ttk.Treeview` with scrollbar) — selecting a row fills the form and stores `self.selected\_shop\_id`.

&#x20; 5. Status label showing clear success/error feedback.

\- Deletion MUST ask `messagebox.askyesno('Confirm Delete', ...)` first.

\- Handle empty list gracefully (display `"No coffee shops found."` in status label without crashing).

\- Handle `HTTPError` (before `URLError`), `socket.timeout`, and `URLError` with `timeout=5`.

\- \*\*Mandatory Tests:\*\* Syntax/import check + automated smoke check + clear manual test checklist for the user (CRUD, empty input error, invalid rating error, stop Flask -> error message -> restart Flask -> retry works without restarting GUI).



\### Phase 4: Extra Feature ("Find My Spot Now") \& Threaded Report Helper

\- Add the \*\*"Find My Spot Now"\*\* panel to `gui\_app.py` (Late Night Only dropdown/check, Vibe selector, Coffee Style selector, `Find My Spot Now` button, `Reset` button) calling `GET /shops/find\_spot` and displaying count + matching shops in the table.

\- Create `report\_helper.py`:

&#x20; - Fetches JSON from `http://127.0.0.1:5050/shops` (`timeout=5`, catches `HTTPError`, `socket.timeout`, `URLError`).

&#x20; - Creates one `threading.Thread` to write a formatted UTF-8 report (`coffee\_shops\_report.txt`) listing all shops, ratings, regions, vibes, late-night status, and summary count using `with open(..., 'w', encoding='utf-8')` inside `try/except OSError`.

&#x20; - Calls `.start()` and `.join()`, then prints clear success/failure result.

\- \*\*Mandatory Tests:\*\* Run `report\_helper.py` while `server.py` is running, verify `coffee\_shops\_report.txt` contents, and verify clean error handling when `server.py` is stopped or file path is invalid.



\### Phase 5: End-to-End Rubric Audit \& `README.md`

\- Run every required final check:

&#x20; 1. Fresh folder / clean start test.

&#x20; 2. Add, view, edit, delete verify only chosen record changes.

&#x20; 3. Persistence check after stopping and restarting Flask + Tkinter.

&#x20; 4. Empty list check (after deleting all rows or using empty filter).

&#x20; 5. Unknown ID check (two Tkinter windows: delete in Window 1, edit in Window 2 -> 404 error shown cleanly).

&#x20; 6. Connection failure \& recovery check (stop Flask -> error -> start Flask -> retry works).

&#x20; 7. Report helper check.

\- Write `README.md` with:

&#x20; - Project summary \& "Find My Spot Now" explanation.

&#x20; - Exact setup commands (`venv`, `pip install -r requirements.txt`, `python setup\_db.py`, `python server.py`, `python gui\_app.py`, `python report\_helper.py`).

&#x20; - \*\*Course Topic Evidence Table\*\* mapping all 8 syllabus topics (Python \& collections, Exceptions, Classes, SQLite, Threads \& files, Tkinter, Client \& server, Flask) to exact file names and function/class names.

&#x20; - Recorded test results from all checks.

&#x20; - Credits \& AI tool disclosure.



\### Phase 6: Oral Defense Cheat Sheet, Slides Outline \& Final Submission Check

\- Generate `CODE\_TRACE\_CHEATSHEET.md`:

&#x20; - Step-by-step trace of one full button click (`Add Shop`: Tkinter -> `urlencode`/`urlopen` -> Flask `request.form` -> `ShopStore.add\_shop` -> SQLite -> JSON reply -> `Treeview` refresh).

&#x20; - Exact line locations for every likely 3-minute live edit (e.g., changing a label, changing rating max limit from 5 to 10, adding a region to dropdown, changing error message text, changing report filename).

\- Generate `SLIDES\_OUTLINE.md` structured for the 10-minute presentation:

&#x20; - Minute 0–1: Idea \& who it helps in Saudi Arabia.

&#x20; - Minute 1–2: Architecture diagram (Tkinter <-> Flask <-> SQLite).

&#x20; - Minute 2–8: Live Demo script (CRUD, filter, "Find My Spot Now", invalid input 400, unknown ID 404, Flask disconnect/recovery, threaded report).

&#x20; - Minute 8–10: Code walkthrough (one Flask route, `ShopStore` class, one parameterized SQL query, GitHub commit history).

\- List exact files to include in `Project\_452048033.zip` (exclude `.venv/`, `\_\_pycache\_\_/`, `AGENT\_GUIDE.md`, `PROGRESS\_HANDOFF.md`, `CODE\_TRACE\_CHEATSHEET.md`, `SLIDES\_OUTLINE.md` unless desired, and exclude any temporary test DBs or passwords).



\---



\## 6. Agent Handoff Protocol (`PROGRESS\_HANDOFF.md`)

At the end of EVERY phase (or before stopping if quota is low), update `PROGRESS\_HANDOFF.md` with:

1\. \*\*Completed Phases:\*\* Checklist of phases done \& verified.

2\. \*\*Files Created / Modified:\*\* List of files with a 1-line summary each.

3\. \*\*Tests Passed:\*\* Exact commands run and pass/fail status.

4\. \*\*Known Issues / Pending Edits:\*\* Anything incomplete or buggy.

5\. \*\*Exact Next Step for Incoming Agent:\*\* The exact phase and first action the next AI agent (e.g., Claude Sonnet 5.5 or Gemini) must execute when resuming.

