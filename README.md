# Midjourney Archiver

This is a command-line tool to download and archive your Midjourney history, including images and full prompt metadata.

## Features

*   Downloads job metadata (prompts, enqueue times, etc.) as JSON and plain text files.
*   Downloads the actual images associated with your jobs.
*   Interactive shell script (`mj-download.sh`) for easy setup and execution.
*   Individual Python scripts (`mj-metadata-archiver.py`, `mj-downloader.py`) for more granular control.
*   Configurable download options (job types, date ranges, overwrite behavior, etc.).
*   Checks for existing files to avoid re-downloading (by default).
*   Supports credentials via environment variables or interactive prompts.

## Installation

1.  **Python:** Make sure you have Python 3.9 or newer installed and available in your system's PATH.
2.  **Download:**
    *   Clone this repository: `git clone https://github.com/your-repo-url/midjourney-archiver.git` (Replace with actual URL if available)
    *   OR Download the source code ZIP and extract it to a folder.
3.  **Dependencies:** Install the required Python package:
    ```bash
    pip install requests
    # or
    pip3 install requests
    ```
    The `mj-download.sh` script will also check for `requests` and remind you if it's missing.

## Usage

There are two main ways to use the archiver:

### 1. Interactive Shell Script (Recommended for most users)

This is the easiest way to get started, especially on Mac or Linux.

```bash
./mj-download.sh
```

The script will:
1.  Check for Python and the `requests` library.
2.  Guide you through obtaining your Midjourney `User ID` and `Session Token` from your browser.
3.  Ask if you want to use credentials found in environment variables (`MIDJOURNEY_USER_ID`, `MIDJOURNEY_SESSION_TOKEN`) if they are set.
4.  Offer to customize various settings for the metadata archival and image downloading process (or use sensible defaults).
5.  Run the metadata archiver.
6.  Run the image downloader.

Follow the on-screen instructions provided by the script.

### 2. Manual Python Script Execution (Advanced)

You can also run the Python scripts directly. This is useful if you are on Windows without a Bash environment, or if you want to automate parts of the process with specific parameters.

**Step 1: Obtain Credentials**

You'll need your Midjourney `User ID` and `__Secure-next-auth.session-token`. The `mj-download.sh` script provides detailed instructions for finding these. Briefly:

1.  Open `https://www.midjourney.com/app/` in a Chromium-based browser (Chrome, Edge, etc.).
2.  Sign in.
3.  Open Developer Tools (F12).
4.  **User ID:** Go to Network > Fetch/XHR. Find a request like `?user_id=YOUR_USER_ID...`. Copy the `YOUR_USER_ID` part.
5.  **Session Token:** Go to Application > Cookies > `https://www.midjourney.com`. Find `__Secure-next-auth.session-token` and copy its value.

You can provide these credentials to the scripts via:
*   Environment variables: `MIDJOURNEY_USER_ID` and `MIDJOURNEY_SESSION_TOKEN`.
*   Command-line arguments: `--user-id` and `--session-token`.
*   Interactive prompts if neither of the above is found.

**Step 2: Run the Metadata Archiver (`mj-metadata-archiver.py`)**

This script crawls your Midjourney history and downloads job metadata.

```bash
python3 ./mj-metadata-archiver.py [OPTIONS]
```

**Common Options:**

*   `--archive-root PATH`: Directory to store metadata (default: `./mj-archive`).
*   `--user-id TEXT`: Your Midjourney User ID.
*   `--session-token TEXT`: Your Midjourney session token.
*   `--page-limit INTEGER`: Limit API pages to crawl (default: all).
*   `--job-type TEXT`: Job type to fetch ('upscale', 'grid', 'all', 'None'; default: 'upscale').
*   `--from-date TEXT`: Start date (YYYY-MM-DD HH:MM:SS.ffffff or YYYY-MM-DD).
*   `--get-from-date-from-archive`: Set `--from-date` from latest in archive.
*   `--overwrite-metadata`: Overwrite existing metadata files.
*   `--json-indent INTEGER`: Indentation for JSON files (0 for compact; default: 2).
*   `--log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]`: Logging verbosity (default: INFO).
*   `--help`: Show help message.

**Example:**

```bash
python3 ./mj-metadata-archiver.py --job-type all --get-from-date-from-archive
```

**Step 3: Run the Image Downloader (`mj-downloader.py`)**

This script walks through the downloaded metadata and downloads the actual images.

```bash
python3 ./mj-downloader.py [OPTIONS]
```

**Common Options:**

*   `--archive-root PATH`: Directory of the metadata archive (default: `./mj-archive`).
*   `--job-types-to-download TEXT`: Comma-separated job types to download images for (e.g., 'upscale,grid', 'all'; default: 'upscale').
*   `--log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]`: Logging verbosity (default: INFO).
*   `--help`: Show help message.

**Example:**

```bash
python3 ./mj-downloader.py --job-types-to-download "upscale,grid"
```

## Folder Structure

The archiver will create a folder structure within your specified archive root (default `mj-archive/`):

```
mj-archive/
└── YYYY/
    └── YYYY-MM/
        └── YYYY-MM-DD/
            ├── YYYYMMDD-HHMMSS_jobid.json
            ├── YYYYMMDD-HHMMSS_jobid.prompt.txt
            ├── YYYYMMDD-HHMMSS_jobid.png
            ├── YYYYMMDD-HHMMSS_jobid-1.png (if multiple images in job)
            └── ...
```

## Disclaimer

This tool interacts with the Midjourney website. Changes to their website or API could break this tool. Use at your own risk. Always respect Midjourney's Terms of Service.

This is alpha software, developed to scratch a personal itch. While efforts have been made to make it robust, there might be bugs.

## License

[MIT License](./LICENSE.txt)

