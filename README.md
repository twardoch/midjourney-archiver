# Midjourney Archive Suite

The Midjourney Archive Suite is a collection of tools designed to help you create a comprehensive local backup of your Midjourney creations. It fetches your job history, including full metadata like prompts and enqueue times, and downloads the corresponding images directly to your computer.

## Part 1: User Guide

### What is the Midjourney Archive Suite?

This suite consists of:
*   **`mj-metadata-archiver.py`**: A Python script to download the metadata for your Midjourney jobs (prompts, job IDs, timestamps, etc.).
*   **`mj-downloader.py`**: A Python script to download the actual images based on the metadata collected by the archiver.
*   **`mj-download.sh`**: A user-friendly shell script (for Linux/macOS) that automates the setup and execution of both Python scripts.

Together, these tools allow you to build a complete, offline archive of your Midjourney generations.

### Who is this for?

This tool is for any Midjourney user who wants:
*   A **local backup** of their generated images and the prompts that created them.
*   An **offline archive** to browse their work without needing internet access or relying on Midjourney's interface.
*   To **analyze their creative process** by having easy access to all prompts and corresponding results.
*   **Protection against potential data loss** if images are ever removed or become inaccessible from Midjourney's servers.

### Why is it useful?

*   **Complete Archival:** Saves both the high-resolution images and the detailed metadata (prompts, job types, parameters) associated with them.
*   **Offline Access:** Browse your entire Midjourney history locally, anytime.
*   **Data Ownership:** Keep your own copy of your creations.
*   **Organization:** Metadata and images are stored in a structured directory format based on date.
*   **Incremental Backups:** The metadata archiver can pick up where it left off, only fetching new jobs since the last run.

### Installation

1.  **Prerequisites:**
    *   **Python:** You need Python 3.9 or newer installed. You can check by running `python --version` or `python3 --version`.
    *   **Git (Recommended):** For easy downloading and updates.

2.  **Download the Suite:**
    *   **With Git (Recommended):**
        ```bash
        git clone <repository_url>
        cd midjourney-archive-suite # Or your chosen directory name
        ```
        (Replace `<repository_url>` with the actual URL of this repository).
    *   **Manual Download:** Download the source code as a ZIP file from the repository page and extract it to a folder on your computer.

3.  **Install Dependencies:**
    The scripts require the `requests` library to communicate with the Midjourney API.
    Navigate to the directory where you downloaded the files and run:
    ```bash
    pip install -r requirements.txt
    ```
    Or, if you use `pip3`:
    ```bash
    pip3 install -r requirements.txt
    ```

### Usage

You can use the tools via the interactive shell script (recommended for ease of use) or by running the Python scripts manually (for more control or automation).

#### Credentials: User ID and Session Token

Both methods require your Midjourney **User ID** and **Session Token** for authentication. Here's how to find them:

1.  Open your web browser (Chromium-based like Chrome, Edge, Brave, Opera is recommended for these instructions) and go to: `https://www.midjourney.com/app/`
2.  Sign in to your Midjourney account if you haven't already.
3.  Open the **Developer Tools**. You can usually do this by pressing `F12`, or right-clicking on the page and selecting 'Inspect' or 'Inspect Element'.

4.  **To get your User ID:**
    *   In Developer Tools, go to the **'Network'** tab.
    *   Make sure **'Fetch/XHR'** is selected as a filter (if available).
    *   Look for a request in the list that starts with `recent-jobs?...` or similar. You might need to scroll or interact with the Midjourney app (e.g., click 'Archive', refresh the page, or scroll through your jobs) to trigger this request.
    *   Select this request. In the **'Headers'** (or 'Request') tab for this request, look at the 'Request URL' or 'Query String Parameters'. You should see `userId=YOUR_USER_ID`. It's a long string of letters and numbers. Copy this value.

5.  **To get your Session Token:**
    *   In Developer Tools, go to the **'Application'** tab (it might be under 'More tabs' or '>>').
    *   On the left side, under 'Storage', expand **'Cookies'** and select `https://www.midjourney.com`.
    *   In the table of cookies, find the cookie named `__Secure-next-auth.session-token`.
    *   Copy its entire **'Cookie Value'**. This is a very long string.

**Important:** Keep your Session Token private, as it grants access to your Midjourney account.

You can provide these credentials to the scripts in three ways (listed by priority):
1.  **Command-line arguments:** `--user-id YOUR_USER_ID --session-token YOUR_TOKEN` (for Python scripts).
2.  **Environment variables:** `MIDJOURNEY_USER_ID` and `MIDJOURNEY_SESSION_TOKEN`.
3.  **Interactive prompt:** If not provided by the above methods, the scripts will ask you to enter them.

#### Method 1: Interactive Shell Script (`mj-download.sh`)

This is the recommended method for most users on Linux or macOS, as it simplifies the process.

1.  **Make it executable (if needed):**
    ```bash
    chmod +x mj-download.sh
    ```
2.  **Run the script:**
    ```bash
    ./mj-download.sh
    ```

The script will:
*   Check if Python and the `requests` library are installed.
*   Guide you on obtaining your User ID and Session Token if you haven't already.
*   Ask if you want to use credentials found in environment variables (if set).
*   Prompt you to enter your User ID and Session Token if they are not found.
*   Offer default settings for archival and download, and allow you to customize them.
*   Execute the `mj-metadata-archiver.py` script to download your job metadata.
*   Execute the `mj-downloader.py` script to download the images.

Follow the on-screen instructions.

#### Method 2: Manual Python Script Execution

This method gives you more granular control and is necessary if you're on Windows (without a Bash environment like WSL or Git Bash) or want to automate the scripts.

**Step 1: Archive Metadata (`mj-metadata-archiver.py`)**

This script connects to Midjourney and downloads the metadata for your jobs.

**Basic Command:**
```bash
python mj-metadata-archiver.py [OPTIONS]
# or
python3 mj-metadata-archiver.py [OPTIONS]
```

**Key Options:**
*   `--archive-root PATH`: Directory to store the metadata (default: `./mj-archive`).
*   `--user-id TEXT`: Your Midjourney User ID.
*   `--session-token TEXT`: Your Midjourney `__Secure-next-auth.session-token`.
*   `--job-type TEXT`: Type of jobs to fetch (e.g., 'upscale', 'grid'). Use 'all' or 'None' to fetch all job types (default: 'upscale').
*   `--from-date TEXT`: Start crawling from this date/time. Format: 'YYYY-MM-DD HH:MM:SS.ffffff', 'YYYY-MM-DD HH:MM:SS', or 'YYYY-MM-DD'. If only date is given, time is assumed as 00:00:00. (Default: Start from the newest jobs).
*   `--get-from-date-from-archive`: Automatically set `--from-date` to the `enqueue_time` of the latest job found in the existing archive. This is useful for incremental backups. Ignored if `--from-date` is explicitly set.
*   `--page-limit INTEGER`: Limit the number of API pages to crawl. Each page typically contains 50 jobs. (Default: crawl all available pages).
*   `--overwrite-metadata`: Overwrite existing metadata files if they are encountered again. (Default: skip existing files).
*   `--json-indent INTEGER`: Indentation level for JSON files. Use `0` for the most compact JSON (no newlines). (Default: `2`).
*   `--log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]`: Set the logging verbosity (default: `INFO`).
*   `--help`: Show this help message and exit.

**Example (archive all job types, incrementally):**
```bash
python mj-metadata-archiver.py --job-type all --get-from-date-from-archive
```
(Assuming User ID and Session Token are set as environment variables or you want to be prompted).

**Step 2: Download Images (`mj-downloader.py`)**

After archiving the metadata, this script downloads the actual images.

**Basic Command:**
```bash
python mj-downloader.py [OPTIONS]
# or
python3 mj-downloader.py [OPTIONS]
```

**Key Options:**
*   `--archive-root PATH`: Root directory of the Midjourney metadata archive (where `mj-metadata-archiver.py` saved its files) (default: `./mj-archive`).
*   `--job-types-to-download TEXT`: Comma-separated list of job types to download images for (e.g., 'upscale,grid'). Provide an empty string or 'all' to download for all types found in metadata. (Default: 'upscale').
*   `--log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]`: Set the logging level (default: `INFO`).
*   `--help`: Show this help message and exit.

**Example (download upscales and grids):**
```bash
python mj-downloader.py --job-types-to-download "upscale,grid"
```

#### Method 3: Programmatic Usage (as Python Modules)

For advanced users or integration into other Python projects, the core logic of the archiver and downloader can be imported and used directly.

You would instantiate `MidjourneyMetadataArchiver` from `mj_metadata_archiver.py` and `MidjourneyDownloader` from `mj_downloader.py`.

**Example: Using `MidjourneyMetadataArchiver`**
```python
from pathlib import Path
from mj_metadata_archiver import MidjourneyMetadataArchiver # Assuming the script is in your PYTHONPATH

# Configuration (replace with your actual values or config mechanism)
USER_ID = "your_user_id"
SESSION_TOKEN = "your_session_token"
ARCHIVE_DIR = Path("./my_custom_mj_archive")

# Ensure archive directory exists
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

archiver = MidjourneyMetadataArchiver(
    archive_root=ARCHIVE_DIR,
    user_id=USER_ID,
    session_token=SESSION_TOKEN,
    json_indent=2
)

print("Starting metadata crawl...")
archiver.crawl(
    job_type="all",  # Fetch all job types
    get_from_date_from_archive=True # Incremental update
)
print(f"Metadata crawl finished. Stats: {archiver.stats}")
```

**Example: Using `MidjourneyDownloader`**
```python
from pathlib import Path
from mj_downloader import MidjourneyDownloader # Assuming the script is in your PYTHONPATH

# Configuration
ARCHIVE_DIR = Path("./my_custom_mj_archive") # Should be the same as used by the archiver

# Specify job types to download, or an empty set for all
job_types_to_get = {"upscale", "grid"}
# For all types with image_paths: job_types_to_get = set()

downloader = MidjourneyDownloader(job_types_to_download=job_types_to_get)

print(f"Starting image download from: {ARCHIVE_DIR}")
downloader.walk_archive(archive_root=ARCHIVE_DIR)
print(f"Image download finished. Stats: {downloader.stats}")
```
When using the classes programmatically, you are responsible for providing all necessary configurations (like credentials, paths, job types) that are normally handled by `argparse` in the scripts or by the `mj-download.sh` wrapper.

### Output Folder Structure

The scripts will organize the downloaded metadata and images into a structured format within your specified archive root (default: `mj-archive/`):

```
mj-archive/
└── YYYY/                     # Year
    └── YYYY-MM/              # Year-Month
        └── YYYY-MM-DD/       # Year-Month-Day (based on job enqueue time)
            ├── YYYYMMDD-HHMMSS_jobid.json          # Full metadata for the job
            ├── YYYYMMDD-HHMMSS_jobid.prompt.txt    # Plain text prompt and full command
            ├── YYYYMMDD-HHMMSS_jobid.png           # Downloaded image (if single image job)
            ├── YYYYMMDD-HHMMSS_jobid-1.png         # First image of a multi-image job (e.g., grid)
            ├── YYYYMMDD-HHMMSS_jobid-2.png         # Second image
            └── ...                                 # etc.
```
The filenames are based on the job's enqueue time and its unique job ID.

## Part 2: Technical Documentation

### How the Code Works

#### `mj-metadata-archiver.py`

This script is responsible for fetching job metadata from Midjourney's API.
1.  **Authentication & Configuration:**
    *   Takes User ID and Session Token as input (CLI args, env vars, or prompt).
    *   Configures parameters like archive root, job types to fetch, date ranges, logging level.
2.  **API Interaction:**
    *   Constructs requests to the Midjourney API endpoint: `https://www.midjourney.com/api/app/recent-jobs/`.
    *   Sends GET requests with appropriate headers (including the session token cookie) and query parameters (user ID, job type, amount, page, fromDate).
    *   The `crawl` method handles pagination, requesting jobs in batches (typically 50 per page).
3.  **Incremental Archiving:**
    *   If `--get-from-date-from-archive` is used, it first scans the existing archive for the latest `enqueue_time` among the already saved JSON files. This time is then used as the `fromDate` for the API request, ensuring only newer jobs are fetched.
4.  **Data Processing & Storage:**
    *   Parses the JSON response from the API. Each item in the list is a job object.
    *   For each job:
        *   Extracts the `enqueue_time` and formats it to create a directory structure: `YYYY/YYYY-MM/YYYY-MM-DD`.
        *   Creates these directories if they don't exist under the specified `archive_root`.
        *   Saves the full job metadata as a JSON file (e.g., `YYYYMMDD-HHMMSS_jobid.json`).
        *   Extracts the `prompt` and `full_command` from the job data and saves them into a separate text file (e.g., `YYYYMMDD-HHMMSS_jobid.prompt.txt`) for quick viewing.
    *   Handles `--overwrite-metadata` to either skip existing files or replace them.
5.  **Logging & Stats:**
    *   Provides logging output (INFO, DEBUG levels) about its progress.
    *   Collects statistics (e.g., jobs processed, types, errors) and prints them at the end.

#### `mj-downloader.py`

This script downloads the actual image files based on the metadata collected by `mj-metadata-archiver.py`.
1.  **Configuration:**
    *   Takes the `archive_root` and a set of `job_types_to_download` as input.
2.  **Archive Traversal:**
    *   The `walk_archive` method recursively scans the `archive_root` directory for `*.json` metadata files.
3.  **Image URL Extraction & Filtering:**
    *   For each JSON file found:
        *   It reads and parses the JSON content.
        *   Checks the job's `type` against the `job_types_to_download` set (if provided; otherwise, processes all jobs with image paths).
        *   If the job type matches (or if downloading all types), it looks for an `image_paths` list in the JSON data. This list contains the direct URLs to the generated images.
4.  **Image Downloading:**
    *   For each URL in `image_paths`:
        *   Constructs a local filename. If a job has multiple images (e.g., a grid), it appends an index (e.g., `-1`, `-2`) to the filename. The extension is derived from the URL or defaults to `.png`.
        *   Checks if the image file already exists at the target path. If so, it skips the download.
        *   If the file doesn't exist, it makes an HTTP GET request to the image URL.
        *   Streams the image content and writes it to a new file in the same directory as its corresponding `.json` metadata file.
5.  **Logging & Stats:**
    *   Logs its actions, including successful downloads, skips, and any errors encountered (HTTP errors, connection issues, file I/O errors).
    *   Collects and displays download statistics upon completion.

#### `mj-download.sh`

This is a Bash shell script that acts as a high-level wrapper for the two Python scripts.
1.  **Environment Checks:**
    *   Verifies if `python` or `python3` is available.
    *   Checks if the `requests` Python module is installed.
2.  **Credential Management:**
    *   Checks for `MIDJOURNEY_USER_ID` and `MIDJOURNEY_SESSION_TOKEN` environment variables.
    *   If not found, or if the user chooses not to use the environment variables, it provides detailed instructions on how to obtain these credentials and prompts the user to input them. These are then exported as environment variables for the Python scripts.
3.  **Configuration:**
    *   Defines default settings for various options of the Python scripts (e.g., archive root, job types).
    *   Optionally allows the user to customize these settings via interactive prompts.
4.  **Script Execution:**
    *   Constructs the command-line arguments for `mj-metadata-archiver.py` based on the (customized) settings.
    *   Executes `mj-metadata-archiver.py`.
    *   If the metadata archiver completes successfully (or if the user chooses to proceed despite errors), it constructs arguments for and executes `mj-downloader.py`.
5.  **Error Handling & Reporting:**
    *   Checks the exit codes of the Python scripts and reports whether they completed successfully or with errors.

### Project Structure

```
.
├── mj-metadata-archiver.py  # Python script for downloading job metadata
├── mj-downloader.py         # Python script for downloading images
├── mj-download.sh           # Shell script for easy setup and execution
├── requirements.txt         # Python package dependencies (requests)
├── README.md                # This file
├── LICENSE.txt              # Project license
├── mj-archive/              # Default output directory for archived data (created by scripts)
│   └── YYYY/
│       └── YYYY-MM/
│           └── YYYY-MM-DD/
│               ├── ...json
│               ├── ...prompt.txt
│               └── ...png
...
```

### Coding and Contribution Rules

We welcome contributions! Please follow these guidelines:

*   **Coding Style:**
    *   Adhere to [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).
    *   Use a linter like Flake8 to check your code.
    *   Keep lines to a reasonable length (e.g., under 100 characters).
*   **Dependencies:**
    *   Keep external dependencies to a minimum.
    *   If a new dependency is essential, add it to `requirements.txt` and justify its inclusion.
*   **Error Handling & Logging:**
    *   Implement robust error handling. Catch specific exceptions where possible.
    *   Use the `logging` module for output. Provide informative error messages and appropriate log levels (DEBUG, INFO, WARNING, ERROR).
*   **API Interaction:**
    *   Be mindful of the Midjourney API. Avoid making overly frequent requests.
    *   Currently, the script doesn't implement explicit rate limiting, but this could be a valuable contribution.
*   **Testing (Aspirational):**
    *   While the project currently lacks automated tests, contributions of new features or significant refactors should ideally be accompanied by unit tests or integration tests.
    *   Consider using Python's `unittest` or `pytest` frameworks.
*   **Commit Messages:**
    *   Follow conventional commit message style (e.g., imperative mood: "Add feature X", "Fix bug Y").
    *   Provide a concise subject line and a more detailed body if necessary.
*   **Pull Requests (PRs):**
    *   Create PRs against the `main` branch (or a designated development branch if one exists).
    *   Clearly describe the changes made and the problem they solve.
    *   Reference any related issues (e.g., "Closes #123").
    *   Ensure your code is well-commented, especially for complex logic.
*   **Environment Variables:**
    *   If introducing new configurable parameters that can be set via environment variables, document them clearly in the README.
*   **Compatibility:**
    *   Aim for compatibility with Python 3.9 and above.

### Disclaimer

This tool interacts with Midjourney's web services. Changes to their website or API could break this tool at any time. The developers of this tool are not responsible for any issues that may arise from its use, including (but not limited to) account suspension or data loss.

**Always respect Midjourney's Terms of Service.** This tool is intended for personal, archival purposes of content you have legitimately generated.

This software is provided "as-is", without warranty of any kind. Use at your own risk.

## License

This project is licensed under the [MIT License](./LICENSE.txt).
