# TODO

This file tracks specific tasks to be completed.

## Phase 1: Core Functionality and Refinements

### `mj-metadata-archiver.py`
- [ ] Implement `argparse` for CLI arguments:
    - [ ] `archive_root` (default: `./mj-archive`)
    - [ ] `user_id` (prompt if not provided or in env/config)
    - [ ] `session_token` (prompt if not provided or in env/config)
    - [ ] `limit` (default: None, meaning crawl all)
    - [ ] `job_type` (default: 'upscale', allow 'None' for all types)
    - [ ] `from_date` (string, e.g., 'YYYY-MM-DD HH:MM:SS.ffffff' or 'YYYY-MM-DD')
    - [ ] `get_from_date_from_archive` (boolean flag, default: False)
    - [ ] `overwrite_metadata` (boolean flag, default: False)
    - [ ] `json_indent` (integer, default: 2, 0 for compact)
    - [ ] `log_level` (e.g., INFO, DEBUG)
- [ ] Function to find the latest enqueue_time from existing archive if `get_from_date_from_archive` is true.
- [ ] Modify `archive_job_info` to check `overwrite_metadata` before writing files.
- [ ] Adjust `json.dump` indent based on `json_indent`.
- [ ] Improve logging messages and consistency.
- [ ] Gracefully handle API errors (e.g., invalid token, rate limits) with informative messages.

### `mj-downloader.py`
- [ ] Implement `argparse` for CLI arguments:
    - [ ] `archive_root` (default: `./mj-archive`)
    - [ ] `job_types_to_download` (comma-separated string, e.g., "upscale,grid", default: "upscale")
    - [ ] `log_level` (e.g., INFO, DEBUG)
- [ ] Add `try-except` block for `json.loads` in `download_from_metadata_file`.
- [ ] Filter jobs to download based on `job_types_to_download`.
- [ ] Improve logging messages and consistency.

### `mj-download.sh`
- [ ] Check for `MIDJOURNEY_USER_ID` and `MIDJOURNEY_SESSION_TOKEN` in environment variables first. If present, confirm with user if they want to use them or enter new ones.
- [ ] Clarify instructions for finding User ID and Session Token, possibly with screenshots or more detailed steps.
- [ ] Pass relevant arguments (like `archive_root`) to the Python scripts if they are also made configurable in the shell script.

### General
- [ ] Create `CHANGELOG.md`.
- [ ] Create a basic `config.ini` or `config.json` structure.
    - [ ] Document how to use it in `README.md`.
    - [ ] Add functionality to scripts to read defaults from config if it exists.
- [ ] Update `README.md` with new CLI usage for both scripts.
- [ ] Add more inline comments to explain complex logic.
- [ ] Ensure `requirements.txt` is accurate.
- [ ] Add a `.gitignore` entry for the configuration file if it contains sensitive info and is not meant to be committed.

## Phase 2: Advanced Features
- [ ] **Incremental Archiving (`mj-metadata-archiver.py`):**
    - [ ] Store/retrieve last successful `enqueue_time` or job ID.
    - [ ] Adjust `from_date` logic to use this for subsequent runs.
- [ ] **Filtering/Searching:** (Further define scope)
- [ ] **Rate Limiting/Retries:**
    - [ ] Implement `time.sleep` after API requests.
    - [ ] Add retry logic for `requests.get` with exponential backoff.
- [ ] **Reporting/Stats:**
    - [ ] More detailed breakdown of downloaded/skipped items.

## Phase 3: Packaging and Distribution
- [ ] **Packaging:**
    - [ ] Create `setup.py` or `pyproject.toml`.
- [ ] **Testing:**
    - [ ] Write unit tests for core functions (e.g., API request logic, metadata parsing).

## Notes
* Review hardcoded limit `limit=10` in `mj-metadata-archiver.py` `main()` and ensure it's driven by CLI/config.
* Review `TODO` comments within the Python scripts and integrate them into this list or address them.
    - `mj-downloader.py`: `TODO: option to decide which types/jobs to download?` (Covered)
    - `mj-downloader.py`: `TODO: try-except for json.loads` (Covered)
    - `mj-metadata-archiver.py`: `TODO: option to get from_date from existing archive?` (Covered)
    - `mj-metadata-archiver.py`: `TODO: there seems to be a hard limit of 2500 items in total job listing` (Document this limitation)
    - `mj-metadata-archiver.py`: `TODO: option to stop crawling if listing was already fully archived` (Related to incremental archiving)
    - `mj-metadata-archiver.py`: `TODO: option to not/force overwriting existing metadata files?` (Covered)
    - `mj-metadata-archiver.py`: `TODO: option to set indent/compactness?` (Covered)
    - `mj-metadata-archiver.py` & `mj-downloader.py`: `TODO: real CLI user interface` (Covered by `argparse` implementation)
