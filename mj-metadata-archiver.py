#!/usr/bin/env python
"""
Python command line tool to download Midjourney job metadata:
- text file with prompt used for each job
- JSON dump with full job metadata listing
"""

import argparse
import collections
import datetime as dt
import itertools
import json
import logging
import os
import textwrap
from pathlib import Path

import requests

_log = logging.getLogger(__name__)


class MidjourneyMetadataArchiver:
    _text_wrapper = textwrap.TextWrapper(
        width=80,
        initial_indent=" " * 4,
        subsequent_indent=" " * 4,
        break_long_words=False,
        break_on_hyphens=False,
    )

    def __init__(self, archive_root: Path, user_id: str, session_token: str, json_indent: int = 2):
        self.archive_root = archive_root
        self.user_id = user_id
        self.session_token = session_token
        self.json_indent = json_indent if json_indent > 0 else None # json.dump indent must be non-negative or None
        self.stats = collections.Counter()

    def request_recent_jobs(
        self,
        job_type: str | None = "upscale",
        from_date: dt.datetime | None = None,
        page: int | None = None,
        amount: int = 50,
    ) -> list[dict]:
        """
        Do `recent-jobs` request to midjourney API
        """
        url = "https://www.midjourney.com/api/app/recent-jobs/"
        params = {
            "amount": amount,
            "orderBy": "new",
            "jobStatus": "completed",
            "userId": self.user_id,
            "dedupe": "true", # Removed space
            "refreshApi": "0", # Changed to string
        }
        if job_type and job_type.lower() != "all": # Add jobType only if specified and not 'all'
            params["jobType"] = job_type
        if from_date:
            params["fromDate"] = from_date # API expects string like "2023-10-26 18:19:40.038313"
        if page:
            params["page"] = str(page) # Changed to string

        headers = {
            "Cookie": f"__Secure-next-auth.session-token={self.session_token}",
        }

        _log.info(f"Requesting recent jobs: {url} with params: {params}")
        try:
            resp = requests.get(url=url, params=params, headers=headers)
            resp.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
        except requests.exceptions.RequestException as e:
            _log.error(f"API request failed: {e}")
            return [] # Return empty list on failure

        if not resp.headers["Content-Type"].startswith("application/json"):
            _log.error(f"Unexpected Content-Type: {resp.headers['Content-Type']}")
            return []

        try:
            job_listing = resp.json()
        except json.JSONDecodeError as e:
            _log.error(f"Failed to decode JSON response: {e}")
            _log.debug(f"Response text: {resp.text}")
            return []

        if isinstance(job_listing, list):
            if not job_listing: # Empty list is a valid response (no jobs found)
                _log.info("Received empty job listing (no jobs found or end of list).")
                return []
            if isinstance(job_listing[0], dict) and all(f in job_listing[0] for f in ["id", "enqueue_time", "prompt"]):
                _log.info(f"Got job listing with {len(job_listing)} jobs.")
                return job_listing
            if job_listing[0] == {"msg": "No jobs found."}:
                _log.info("Response: 'No jobs found'")
                return []

        _log.warning(f"Unexpected job listing format: {job_listing}")
        return []


    def get_latest_enqueue_time_from_archive(self) -> Optional[str]:
        """
        Finds the latest enqueue_time from existing JSON files in the archive.
        Returns None if no files are found or if times cannot be parsed.
        """
        latest_time_obj = None
        latest_time_str = None

        for json_file in self.archive_root.glob("**/*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                enqueue_time_str = data.get("enqueue_time")
                if enqueue_time_str:
                    # Standard format: "2023-10-26 18:19:40.038313"
                    # Sometimes it might be without microseconds: "2023-10-26 18:19:40"
                    try:
                        current_time_obj = dt.datetime.strptime(enqueue_time_str, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        try:
                            current_time_obj = dt.datetime.strptime(enqueue_time_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            _log.warning(f"Could not parse enqueue_time '{enqueue_time_str}' from {json_file}")
                            continue

                    if latest_time_obj is None or current_time_obj > latest_time_obj:
                        latest_time_obj = current_time_obj
                        latest_time_str = enqueue_time_str
            except json.JSONDecodeError:
                _log.warning(f"Could not decode JSON from {json_file}")
            except Exception as e:
                _log.warning(f"Error processing file {json_file}: {e}")

        if latest_time_str:
            _log.info(f"Latest enqueue_time found in archive: {latest_time_str}")
        else:
            _log.info("No existing enqueue_time found in archive.")
        return latest_time_str

    def crawl(
        self,
        limit: int | None = None,
        job_type: str | None = "upscale",
        from_date: str | None = None,
    ):
        """
        Crawl the Midjourney API to collect job metadata
        """
        if get_from_date_from_archive and from_date is None:
            # Only get from archive if from_date is not explicitly set.
            # This allows overriding the archive's latest time if needed.
            archived_from_date = self.get_latest_enqueue_time_from_archive()
            if archived_from_date:
                from_date = archived_from_date
                _log.info(f"Using from_date from archive: {from_date}")

        # TODO: there seems to be a hard limit of 2500 items in total job listing (document this)
        pages = range(1, page_limit + 1) if page_limit else itertools.count(1)
        initial_from_date = from_date # Store the initial from_date for consistent paging

        for page in pages:
            _log.info(f"Crawling for job info batch page={page}")
            job_listing = self.request_recent_jobs(
                from_date=initial_from_date, page=page, job_type=job_type
            )
            if not job_listing:
                _log.info("Empty job listing batch: reached end of total job listing or API error.")
                break

            new_jobs_archived_this_page = self.archive_job_listing(job_listing, overwrite_metadata)

            # TODO: option to stop crawling if listing was already fully archived
            # If overwrite_metadata is False and no new jobs were archived on this page,
            # and we are using from_date from archive, it implies we might have caught up.
            # However, new jobs could have been added *after* the from_date but before current time.
            # A more robust "already fully archived" check would require knowing the *very latest* job ID from API,
            # or if the API simply returns no new jobs for a from_date that was the newest in our archive.
            # For now, if overwrite is false and nothing new saved, and we are using archive date, we can stop.
            if not overwrite_metadata and new_jobs_archived_this_page == 0 and get_from_date_from_archive:
                 _log.info("No new jobs archived on this page and using from_date from archive. Assuming up to date.")
                 # break # Be cautious with this break, it might be too aggressive if jobs were added between archive time and now.
                         # The API returning an empty list is the more reliable stop condition.

            # Get "enqueue_time" of the *first* job in the *first ever* batch for consistent paging in subsequent requests.
            # The API uses the fromDate of the *first job on the first page* as a reference for subsequent pages.
            if initial_from_date is None and job_listing:
                initial_from_date = job_listing[0]["enqueue_time"]
                _log.info(f"Set initial_from_date for paging: {initial_from_date}")

    def archive_job_listing(self, job_listing: list[dict]):
        for job_info in job_listing:
            if self.archive_job_info(job_info, overwrite_metadata):
                archived_count += 1
        return archived_count

    def archive_job_info(self, job_info: dict, overwrite_metadata: bool) -> bool:
        job_id = job_info["id"]
        enqueue_time = job_info["enqueue_time"]
        _log.info(f"Archiving metadata of job {job_id} ({enqueue_time=})")

        self.stats["job_processed"] += 1
        self.stats[f"job_type_{job_info.get('type', 'unknown')}"] += 1

        try:
            # Attempt to parse with microseconds
            enqueue_time_dt = dt.datetime.strptime(enqueue_time, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            # Fallback to parsing without microseconds
            try:
                enqueue_time_dt = dt.datetime.strptime(enqueue_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                _log.error(f"Could not parse enqueue_time '{enqueue_time}' for job {job_id}. Skipping archiving of this job.")
                self.stats["error_parsing_enqueue_time"] += 1
                return False # Indicates failure to archive this specific job

        job_dir = self.archive_root / enqueue_time_dt.strftime("%Y/%Y-%m/%Y-%m-%d")
        try:
            job_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            _log.error(f"Could not create directory {job_dir}: {e}. Skipping archiving of job {job_id}.")
            self.stats["error_creating_directory"] += 1
            return False

        filename_base = f"{enqueue_time_dt.strftime('%Y%m%d-%H%M%S')}_{job_id}"
        json_path = job_dir / f"{filename_base}.json"
        prompt_path = job_dir / f"{filename_base}.prompt.txt"

        if not overwrite_metadata and json_path.exists() and prompt_path.exists():
            _log.debug(f"Skipping job {job_id}, metadata files already exist and overwrite_metadata is False.")
            self.stats["skipped_existing"] += 1
            return False # Indicates that the job was not newly archived, but existed

        # Store raw metadata as JSON file
        try:
            with json_path.open("w", encoding="utf-8") as f:
                json.dump(job_info, f, indent=self.json_indent)
        except IOError as e:
            _log.error(f"Error writing JSON file {json_path}: {e}")
            self.stats["error_writing_json"] += 1
            return False # Failed to archive

        # Store prompt info as text file
        try:
            with prompt_path.open("w", encoding="utf-8") as f:
                f.write("Prompt:\n")
                # Use .get() for prompt and full_command in case they are missing from job_info
                f.write(self._text_wrapper.fill(job_info.get("prompt", "[No Prompt Available]")) + "\n")
                f.write("\nFull command:\n")
                f.write(self._text_wrapper.fill(job_info.get("full_command", "[No Full Command Available]")) + "\n")
        except IOError as e:
            _log.error(f"Error writing prompt file {prompt_path}: {e}")
            self.stats["error_writing_prompt"] += 1
            # If JSON was written but prompt failed, we count it as partially archived.
            # The function should probably still return False as it wasn't a full success.
            if json_path.exists():
                 self.stats["archived_json_only_prompt_failed"] +=1
            return False

        self.stats["archived_newly"] +=1
        return True # Indicates that the job was newly and successfully archived


def main():
    parser = argparse.ArgumentParser(
        description="Download Midjourney job metadata.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Provides default values in help message
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=Path.cwd() / "mj-archive",
        help="Root directory for storing archived metadata.",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=os.environ.get("MIDJOURNEY_USER_ID"),
        help="Your Midjourney User ID. Can also be set via MIDJOURNEY_USER_ID environment variable.",
    )
    parser.add_argument(
        "--session-token",
        type=str,
        default=os.environ.get("MIDJOURNEY_SESSION_TOKEN"),
        help="Your Midjourney __Secure-next-auth.session-token. Can also be set via MIDJOURNEY_SESSION_TOKEN environment variable.",
    )
    parser.add_argument(
        "--page-limit",
        type=int,
        default=None,
        help="Limit the number of API pages to crawl. Each page typically contains 50 jobs. Default: crawl all available pages."
    )
    parser.add_argument(
        "--job-type",
        type=str,
        default="upscale",
        help="Type of jobs to fetch (e.g., 'upscale', 'grid'). Use 'all' or 'None' to fetch all job types.",
    )
    parser.add_argument(
        "--from-date",
        type=str,
        default=None,
        help="Start crawling from this date/time. Format: 'YYYY-MM-DD HH:MM:SS.ffffff' or 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'. "
             "If only date is given, time is assumed as 00:00:00. Default: Start from the newest jobs.",
    )
    parser.add_argument(
        "--get-from-date-from-archive",
        action="store_true",
        help="Automatically set --from-date to the enqueue_time of the latest job found in the existing archive. "
             "This is ignored if --from-date is explicitly set.",
    )
    parser.add_argument(
        "--overwrite-metadata",
        action="store_true",
        help="Overwrite existing metadata files if they are encountered again. Default: False (skip existing files).",
    )
    parser.add_argument(
        "--json-indent",
        type=int,
        default=2,
        help="Indentation level for JSON files. Use 0 for the most compact JSON output (no newlines or spaces).",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level.",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )

    user_id = args.user_id
    if not user_id:
        try:
            user_id = input("Enter your Midjourney User ID: ")
        except EOFError: # Handle non-interactive execution (e.g. cronjob)
            _log.error("User ID not provided via --user-id argument, MIDJOURNEY_USER_ID environment variable, or interactive prompt.")
            return 1 # Exit with error code

    session_token = args.session_token
    if not session_token:
        try:
            session_token = input("Enter your Midjourney Session Token (__Secure-next-auth.session-token): ")
        except EOFError:
            _log.error("Session Token not provided via --session-token argument, MIDJOURNEY_SESSION_TOKEN environment variable, or interactive prompt.")
            return 1

    if not user_id or not session_token:
        # This case should ideally be caught by the individual checks above, but as a safeguard:
        _log.error("User ID and Session Token are required.")
        return 1

    # Validate from_date format if provided, before passing to the archiver
    parsed_from_date = None
    if args.from_date:
        try:
            parsed_from_date = dt.datetime.strptime(args.from_date, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            try:
                parsed_from_date = dt.datetime.strptime(args.from_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # Allow just date, assume midnight
                    parsed_from_date = dt.datetime.strptime(args.from_date, "%Y-%m-%d")
                except ValueError:
                    _log.error(f"Invalid --from-date format: '{args.from_date}'. Use 'YYYY-MM-DD HH:MM:SS.ffffff', 'YYYY-MM-DD HH:MM:SS', or 'YYYY-MM-DD'.")
                    return 1

    # For the API call, we need the from_date as a string in the specific format it expects,
    # or None if not applicable. The internal logic of request_recent_jobs handles the string.
    from_date_for_api = args.from_date

    job_type_to_pass = args.job_type
    if args.job_type and args.job_type.lower() in ["all", "none"]:
        job_type_to_pass = None # API expects null or no jobType param for all types
        _log.info("Attempting to fetch all job types.")
    else:
        _log.info(f"Attempting to fetch job type: {job_type_to_pass}")

    resolved_archive_root = args.archive_root.resolve()
    try:
        resolved_archive_root.mkdir(parents=True, exist_ok=True)
        _log.info(f"Archive root set to: {resolved_archive_root}")
    except OSError as e:
        _log.error(f"Could not create archive root directory {resolved_archive_root}: {e}")
        return 1


    metadata_archiver = MidjourneyMetadataArchiver(
        archive_root=resolved_archive_root,
        user_id=user_id,
        session_token=session_token,
        json_indent=args.json_indent,
    )
    try:
        metadata_archiver.crawl(
            page_limit=args.page_limit,
            job_type=job_type_to_pass,
            from_date=from_date_for_api,
            get_from_date_from_archive=args.get_from_date_from_archive,
            overwrite_metadata=args.overwrite_metadata,
        )
    except KeyboardInterrupt:
        _log.info("Caught KeyboardInterrupt. Exiting gracefully.")
    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            if e.response.status_code == 401:
                _log.error(f"HTTP 401 Unauthorized: API request failed. This often means your session token is invalid or expired.")
            elif e.response.status_code == 403:
                 _log.error(f"HTTP 403 Forbidden: API request failed. Check your User ID and permissions. It's also possible the API structure changed or access was revoked.")
            else:
                _log.error(f"HTTP Error during API request: {e.response.status_code} - {e.response.text}")
        else:
            _log.error(f"HTTP Error during API request (no response object): {e}")
    except requests.exceptions.RequestException as e:
        _log.error(f"A network error occurred during API request: {e}")
    except Exception as e:
        _log.error(f"An unexpected error occurred: {e}", exc_info=True) # Log full traceback for truly unexpected errors
    finally:
        _log.info(f"Archiving process finished. Stats: {metadata_archiver.stats}")
        if metadata_archiver.stats.get("error_parsing_enqueue_time",0) > 0 or \
           metadata_archiver.stats.get("error_creating_directory",0) > 0 or \
           metadata_archiver.stats.get("error_writing_json",0) > 0 or \
           metadata_archiver.stats.get("error_writing_prompt",0) > 0:
            return 1 # Exit with error code if any file operation errors occurred
        return 0 # Exit with success code


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
