# Saudi Coffee Shop Guide

**Course:** Advanced Programming 462 — individual Client–Server project
**Language:** Python 3 (standard library + Flask)

## 1. Project Overview

The Saudi Coffee Shop Guide is a desktop app for browsing and managing coffee shops across Saudi Arabia (Riyadh, Jeddah, Madinah, Eastern Province, AlUla, Asir).

You can add, view, edit, delete and filter coffee shops in a Tkinter window. The window never touches the database. Every action is sent as an HTTP request to a Flask server, and only the server reads and writes the SQLite database.

```
Tkinter GUI (gui_app.py)  <--HTTP / JSON-->  Flask server (server.py, port 5050)  <-->  SQLite (shop_store.py -> coffee_shops.db)
```

### Extra Feature: "Find My Spot Now" (Late-Night & Vibe Spot Finder)

Many cafes in Saudi Arabia stay open past midnight, and people choose a cafe for its atmosphere as much as its coffee. The **Find My Spot Now** panel finds matching cafes in one click using three choices:

| Choice | Options |
|---|---|
| Late Night | Any / Yes (open past midnight or 24h) |
| Vibe | Any / Quiet Study / Social Hangout / Family Seating / Drive-Thru |
| Coffee Style | Any / Saudi Qahwa / V60 / Specialty / Espresso & Dessert |

The GUI calls `GET /shops/find_spot`. The server runs `ShopStore.find_spot_now()`, which returns the matches sorted by highest rating first. The table shows the matches and the status label shows how many were found. **Reset** returns to the full list.

## 2. Project Files

| File | Purpose |
|---|---|
| `shop_store.py` | `ShopStore` class: SQLite table creation, CRUD, filtering, Find My Spot Now query, sample seeding |
| `setup_db.py` | Creates the table and seeds 6 sample shops **only if the table is empty** |
| `server.py` | Flask JSON API on `127.0.0.1:5050` |
| `gui_app.py` | Tkinter desktop app (`CoffeeGuideWindow`) |
| `report_helper.py` | Terminal script that writes `coffee_shops_report.txt` using a thread |
| `tests/test_store.py` | Automated tests for `ShopStore` |
| `tests/test_api.py` | Automated HTTP tests for all Flask routes |
| `requirements.txt` | `Flask` |

### API Routes

| Method & Route | Purpose | Status codes |
|---|---|---|
| `GET /shops` | All shops, optional `region` and `min_rating` | 200, 400 (bad min_rating), 500 |
| `GET /shops/find_spot` | Find My Spot Now (`open_late`, `seating_vibe`, `coffee_style`) | 200, 500 |
| `POST /shops/add` | Add a shop | 200, 400, 500 |
| `POST /shops/edit` | Edit a shop by `id` | 200, 400, 404, 500 |
| `POST /shops/delete` | Delete a shop by `id` | 200, 400, 404, 500 |

## 3. Setup & Run (Windows PowerShell)

Run these from the project folder.

```powershell
# 1. create and activate the virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. install Flask
pip install -r requirements.txt

# 3. create the database and the 6 sample shops (safe to run again)
python setup_db.py

# 4. start the server (terminal 1, keep it open)
python server.py

# 5. start the desktop app (terminal 2)
python gui_app.py

# 6. write the text report while the server is running (terminal 3)
python report_helper.py
```

To run the automated tests:

```powershell
python tests/test_store.py
python tests/test_api.py
```

> `tests/test_api.py` starts its own server on port 5050 with a temporary database, so stop `server.py` before running it.

## 4. Course Topic Evidence Table

| # | Course Topic | File | Evidence (function / class) |
|---|---|---|---|
| 1 | Python & collections | `shop_store.py`, `server.py`, `gui_app.py`, `report_helper.py` | `SAMPLE_SHOPS` (list of tuples); `ShopStore._row_to_dict` (dict); `ALLOWED_STYLES` / `ALLOWED_VIBES` (tuples) and `validate_shop_form` (dict); `REGIONS`, `STYLES`, `VIBES` lists and `CoffeeGuideWindow.read_form` (dict); `write_report` (list of lines) |
| 2 | Exceptions | `gui_app.py`, `report_helper.py`, `server.py` | `send_request` and `fetch_shops` catch `HTTPError` → `socket.timeout` → `URLError`; `write_report` catches `OSError`; `validate_shop_form` catches `ValueError`; every route catches `sqlite3.Error` and closes the store in `finally:` |
| 3 | Classes | `shop_store.py`, `gui_app.py` | `ShopStore` (data access class); `CoffeeGuideWindow(tk.Tk)` (main window class) |
| 4 | SQLite | `shop_store.py`, `setup_db.py` | `ShopStore.__init__`, `create_table`, `add_shop`, `get_all_shops`, `get_shop_by_id`, `update_shop`, `delete_shop`, `filter_shops`, `find_spot_now`, `seed_sample_shops`, `close`. All SQL uses `?` placeholders, and writes use `with self.conn:`. `setup_database()` in `setup_db.py` |
| 5 | Threads & files | `report_helper.py` | `main()` creates `threading.Thread(target=write_report, args=(...))`, then calls `.start()` and `.join()`; `write_report()` uses `with open(output_path, 'w', encoding='utf-8')` |
| 6 | Tkinter | `gui_app.py` | `CoffeeGuideWindow`: `grid()` layout, `ttk.Treeview(show='headings')` + scrollbar, `ttk.Combobox`, `messagebox.askyesno('Confirm Delete', ...)`, `status_label`; methods `build_form_panel`, `build_find_spot_panel`, `on_row_selected`, `delete_shop` |
| 7 | Client & server | `gui_app.py`, `report_helper.py` | `send_request(path, form_data=None)` uses `urlopen(url, timeout=5)` for GET and `urlencode(...).encode('utf-8')` for POST; `json.loads(reply.read().decode('utf-8'))`; `fetch_shops()` |
| 8 | Flask | `server.py` | `app = Flask(__name__)`; `@app.route` functions `get_shops`, `find_spot`, `add_shop`, `edit_shop`, `delete_shop`; `request.form` / `request.args`; `jsonify`; `make_error`; a fresh `ShopStore(DB_PATH)` per request |

## 5. Recorded Test Results

All results below were recorded with the project's `.venv` Python (3.14.7, Flask 3.1.3).

### Automated unit / API tests

| Command | Result |
|---|---|
| `python tests/test_store.py` | **PASS** — 7 tests (add/read, edit, delete, unknown ID → `None`/`0`, idempotent seeding, region/rating filter, Find My Spot Now) |
| `python tests/test_api.py` | **PASS** — 6 tests (`GET /shops` list + filter; add valid 200; missing name / non-numeric rating / rating 9 → 400; edit valid 200 / ID 99999 → 404; delete valid 200 / ID 99999 → 404; find_spot match + empty result) |
| `python -m py_compile` on all 5 source files | **PASS** |

### End-to-end rubric checks

For these checks, the real `python server.py` was started as a separate process from a fresh copy of the project folder.

| # | Check | Result |
|---|---|---|
| 1 | Fresh folder / clean start | **PASS** — no DB beforehand; `setup_db.py` seeded 6, second run printed `existing records preserved (total: 6)`; server returned 6 shops |
| 2 | Add / view / edit / delete change only the chosen record | **PASS** — added ID 7, edited its rating to 5; the other 6 rows were unchanged |
| 3 | Persistence after restarting Flask | **PASS** — after stop + restart, 7 shops remained, including the added one |
| 4 | Empty list | **PASS** — after deleting every row, the GUI showed 0 rows and `No coffee shops found.`; restarting Flask did **not** re-seed (count stayed 0) |
| 5 | Unknown ID with two windows | **PASS** — Window 1 deleted ID 7; Window 2 then edited it and got `Server error 404: Coffee shop with ID 7 was not found.`, and its stale row was removed |
| 6 | Connection failure & recovery | **PASS** — with Flask stopped, the GUI showed `Cannot connect to the server. Start server.py and try again.`; after restarting Flask, refresh showed `Loaded 6 coffee shop(s).` without restarting the GUI |
| 7 | Report helper | **PASS** — running: `Report SUCCESS: wrote 6 shops to coffee_shops_report.txt`; stopped: `Report FAILED: Cannot connect to the server. Start server.py first.`; invalid path: `Report FAILED: could not write file ([Errno 2] ...)`; empty DB: `wrote 0 shops` |
| — | Delete after deselecting a row | **PASS** — showed the warning `Please select a coffee shop first.` with no crash |

### Manual GUI tests (performed by the student)

CRUD through the buttons, empty input error, invalid rating error, Yes/No delete confirmation, filter and Show All, Find My Spot Now and Reset, and Flask stop → error → restart → retry: **PASS**.

## 6. Credits & AI Assistance Disclosure

- **Student:** Mohamed Ishak Mohamed Ifthikar — Student ID 452048033
- **Course:** Advanced Programming 462 — Dr. Majed Hariri
- **Sample data:** The coffee shop names and notes are illustrative sample data for demonstration.
- **AI assistance:** I used AI coding assistants (Google Antigravity agent, running Gemini and Claude models) to generate code drafts, tests and documentation, phase by phase, following my own phased specification. I reviewed every phase, ran the tests, did the manual GUI checks, and approved and committed each phase myself. I can explain every core line of the code.
