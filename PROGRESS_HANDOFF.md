# PROGRESS_HANDOFF.md — Saudi Coffee Shop Guide

## 1. Completed Phases
- [x] **Phase 1: Project Setup & SQLite Data Layer** — Complete & Verified
- [x] **Phase 2: Flask Back-End API (`server.py`)** — Complete & Verified
- [ ] **Phase 3: Tkinter Core CRUD & Error Handling (`gui_app.py`)** — Pending
- [ ] **Phase 4: Extra Feature ("Find My Spot Now") & Threaded Report Helper** — Pending
- [ ] **Phase 5: End-to-End Rubric Audit & `README.md`** — Pending
- [ ] **Phase 6: Oral Defense Cheat Sheet, Slides Outline & Final Submission Check** — Pending

---

## 2. Files Created / Modified
- `.gitignore` — Ignores `.venv/`, `__pycache__/`, `*.pyc`, `coffee_shops_report.txt`, and `*.db`.
- `requirements.txt` — Lists `Flask` as the only external dependency.
- `shop_store.py` — Implements `ShopStore` with parameterized `sqlite3` CRUD, `filter_shops`, `find_spot_now`, `seed_sample_shops`, and `close`.
- `setup_db.py` — Standalone setup script creating `coffee_shops` table (`IF NOT EXISTS`) and seeding the 6 sample Saudi coffee shops only when empty.
- `tests/test_store.py` — Unit tests on a temporary SQLite DB covering add, read, edit, delete, unknown ID (`None`/`0`), idempotent seeding, region/rating filtering, and Find My Spot Now filtering.
- `server.py` — Flask JSON API server on `127.0.0.1:5050` with `validate_shop_form(form)` and routes `GET /shops`, `GET /shops/find_spot`, `POST /shops/add`, `POST /shops/edit`, and `POST /shops/delete`, opening and closing a fresh `ShopStore(DB_PATH)` per request inside `try / finally`.
- `tests/test_api.py` — Automated HTTP API tests using `urllib.request.urlopen` and `urllib.parse.urlencode` against a live server on `127.0.0.1:5050` backed by a temporary SQLite database.
- `PROGRESS_HANDOFF.md` — Tracks completed phases, created files, test results, and next steps.

---

## 3. Tests Passed
- `.\.venv\Scripts\python.exe setup_db.py` (1st & 2nd runs): **PASS** — 6 sample rows seeded once and preserved on repeat runs.
- `.\.venv\Scripts\python.exe tests/test_store.py`: **PASS** — `Ran 7 tests in 0.057s` (`OK`).
- `.\.venv\Scripts\python.exe tests/test_api.py`: **PASS** — `Ran 6 tests in 0.329s` (`OK`: `test_add_shop_valid`, `test_add_shop_validation_errors`, `test_delete_shop_valid_and_unknown_id`, `test_edit_shop_valid_and_unknown_id`, `test_find_spot_endpoint`, `test_get_shops`).

---

## 4. Known Issues / Pending Edits
- None for Phases 1 and 2.

---

## 5. Exact Next Step for Incoming Agent
Start **Phase 3: Tkinter Core CRUD & Error Handling (`gui_app.py`)**:
1. Create `gui_app.py` with `CoffeeGuideWindow(tk.Tk)` and helper `send_request(path, form_data=None)` targeting `http://127.0.0.1:5050` with `timeout=5` and catching `HTTPError`, `socket.timeout`, and `URLError` in that exact order.
2. Build the `grid()` layout with all required widget names (`name_entry`, `region_combo`, `rating_entry`, `style_combo`, `vibe_combo`, `open_late_combo`, `notes_entry`, `shops_table`, `status_label`, `add_button`, `edit_button`, `delete_button`) plus filter bar, row selection into form (`self.selected_shop_id`), `messagebox.askyesno` delete confirmation, and empty-list status message (`"No coffee shops found."`).
3. Run syntax/import checks, automated smoke verification, and provide the user with the Phase 3 manual test checklist.
