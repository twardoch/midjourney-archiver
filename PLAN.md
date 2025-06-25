# Plan

This document outlines the plan for improving the Midjourney Archiver project.

## Phase 1: Core Functionality and Refinements

1.  **Improve CLI for `mj-metadata-archiver.py` and `mj-downloader.py`:**
    *   Use a proper CLI library (e.g., `argparse` or `click`).
    *   Allow specifying `archive_root` via command-line argument.
    *   For `mj-metadata-archiver.py`:
        *   Allow specifying `limit`, `job_type`, `from_date` via CLI.
        *   Option to get `from_date` from existing archive.
        *   Option to control overwriting of existing metadata files.
        *   Option to set JSON indent/compactness.
    *   For `mj-downloader.py`:
        *   Option to decide which job types/jobs to download.
2.  **Enhance `mj-download.sh`:**
    *   Improve user prompts and instructions.
    *   Potentially detect OS and provide more specific browser instructions.
    *   Optionally, attempt to read credentials from environment variables first.
3.  **Error Handling and Robustness:**
    *   Add `try-except` for `json.loads` in `mj-downloader.py`.
    *   Improve error messages and logging across both scripts.
    *   Handle potential API changes or unexpected responses more gracefully in `mj-metadata-archiver.py`.
4.  **Configuration File:**
    *   Introduce a configuration file (e.g., `config.json` or `config.ini`) to store default values for CLI options, user ID, and session token (with appropriate security warnings).
5.  **Documentation:**
    *   Update `README.md` with new CLI usage, configuration file details, and any other changes.
    *   Add comments within the code for better understanding.
6.  **Dependency Management:**
    *   Ensure `requirements.txt` is up-to-date.
    *   Consider using a virtual environment.

## Phase 2: Advanced Features

1.  **Incremental Archiving:**
    *   Modify `mj-metadata-archiver.py` to intelligently fetch only new jobs since the last run. This would likely involve storing the timestamp or ID of the last fetched job.
2.  **Filtering and Searching:**
    *   Add options to filter jobs based on keywords in prompts or other metadata fields.
    *   Provide a way to search the local archive.
3.  **Rate Limiting and Retries:**
    *   Implement more sophisticated rate limiting to avoid overloading the Midjourney API.
    *   Add automatic retries for failed downloads or API requests with backoff.
4.  **Reporting and Stats:**
    *   Enhance the stats displayed at the end of script execution.
    *   Option to generate a summary report of the archive.
5.  **GUI (Optional):**
    *   Consider developing a simple GUI for easier use, though this is a lower priority.

## Phase 3: Packaging and Distribution

1.  **Packaging:**
    *   Package the tool for easier distribution (e.g., using PyPI).
2.  **Testing:**
    *   Write unit tests for key components.
    *   Consider integration tests.

## Ongoing Tasks

*   Keep `TODO.md` updated with specific tasks derived from this plan.
*   Record all significant changes in `CHANGELOG.md`.
*   Continuously refine code for elegance, efficiency, and readability.
*   Ensure build tooling (if any introduced) is kept in sync.
