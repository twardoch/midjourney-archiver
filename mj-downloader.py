#!/usr/bin/env python
"""
Python command line tool to download images linked from
Midjourney metadata archive.
"""

import collections
import json
import logging
from pathlib import Path
from typing import Set

import requests

_log = logging.getLogger(__name__)


class MidjourneyDownloader:
    def __init__(self, job_types_to_download: Set[str]):
        self.stats = collections.Counter()
        self.job_types_to_download = job_types_to_download
        if not self.job_types_to_download: # Download all if empty set is passed
            _log.info("No specific job types provided, will attempt to download for all types with image_paths.")


    def walk_archive(self, archive_root: Path):
        _log.info(f"Walking through archive root: {archive_root}")
        json_files = list(archive_root.glob("**/*.json"))
        if not json_files:
            _log.warning(f"No JSON metadata files found in {archive_root} or its subdirectories.")
            return

        for job_info_path in json_files:
            _log.debug(f"Processing metadata file: {job_info_path}")
            self.download_from_metadata_file(job_info_path)

    def download_from_metadata_file(self, job_info_path: Path):
        try:
            job_info_text = job_info_path.read_text(encoding="utf8")
            job_info = json.loads(job_info_text)
        except json.JSONDecodeError as e:
            _log.error(f"Error decoding JSON from {job_info_path}: {e}")
            self.stats["error_json_decode"] += 1
            return
        except IOError as e:
            _log.error(f"Error reading file {job_info_path}: {e}")
            self.stats["error_file_read"] += 1
            return

        job_id = job_info.get("id", "unknown_id")
        job_type = job_info.get("type")

        if not job_type:
            _log.warning(f"Job type missing in metadata file {job_info_path} for job ID {job_id}. Skipping.")
            self.stats["skipped_missing_type"] += 1
            return

        if self.job_types_to_download and job_type not in self.job_types_to_download:
            _log.debug(f"Skipping job ID {job_id} of type '{job_type}', not in specified types to download: {self.job_types_to_download}")
            self.stats[f"skipped_type_{job_type}"] += 1
            return

        self.stats[f"processed_type_{job_type}"] += 1

        image_paths = job_info.get("image_paths")
        if not image_paths:
            _log.debug(f"No 'image_paths' found in metadata for job ID {job_id} ({job_info_path}). Skipping.")
            self.stats["skipped_no_image_paths"] += 1
            return

        if not isinstance(image_paths, list):
            _log.warning(f"'image_paths' in {job_info_path} for job ID {job_id} is not a list. Skipping.")
            self.stats["skipped_invalid_image_paths_format"] += 1
            return

        for i, image_url in enumerate(image_paths):
            if not isinstance(image_url, str) or not image_url.startswith("http"):
                _log.warning(f"Invalid image URL '{image_url}' for job ID {job_id} in {job_info_path}. Skipping this image.")
                self.stats["skipped_invalid_image_url"] +=1
                continue

            try:
                # Basic extension check, can be improved
                extension = Path(image_url.split("?")[0]).suffix.lstrip('.').lower()
                if not extension: # If URL has no extension like some discord URLs
                    # Attempt to guess from content-type or default to a common one later if needed
                    # For now, we rely on Midjourney typically providing .png
                    _log.debug(f"Image URL '{image_url}' has no clear extension. Will proceed and hope for the best.")
                    # Use a default if truly stuck, or let the server's Content-Type guide (more complex)
                    extension = "png" # Defaulting to png as it's common for Midjourney

                if extension not in ["png", "jpg", "jpeg", "webp"]: # Added webp as it's also used
                    _log.warning(f"Unsupported image extension '{extension}' from URL {image_url} for job {job_id}. Skipping this image.")
                    self.stats[f"skipped_unsupported_extension_{extension}"] += 1
                    continue
            except Exception as e:
                _log.error(f"Error processing image URL '{image_url}' for extension: {e}. Skipping this image.")
                self.stats["error_processing_url_extension"] +=1
                continue

            image_index_suffix = "" if len(image_paths) == 1 else f"-{i + 1}"
            # Construct filename based on the JSON filename stem + index + extension
            # e.g., 20231027-123456_jobid.json -> 20231027-123456_jobid-1.png
            download_filename = f"{job_info_path.stem}{image_index_suffix}.{extension}"
            download_path = job_info_path.parent / download_filename

            if download_path.exists():
                _log.debug(f"Image already exists, skipping: {download_path}")
                self.stats["skipped_already_exists"] += 1
            else:
                self.download_url(image_url, download_path, job_id)

    def download_url(self, url: str, path: Path, job_id: str):
        _log.info(f"Downloading for job {job_id}: {path.name} from {url}")
        try:
            with requests.get(url, stream=True, timeout=30) as response: # Added timeout
                response.raise_for_status()
                # TODO: Potentially check Content-Type header here to verify image format if extension was guessed
                with path.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=8192): # Use a common chunk size
                        f.write(chunk)
                self.stats["downloaded_successfully"] += 1
                _log.debug(f"Successfully downloaded {path.name}")
        except requests.exceptions.HTTPError as e:
            _log.error(f"HTTP error downloading {url} for job {job_id}: {e}")
            self.stats["error_http"] += 1
        except requests.exceptions.ConnectionError as e:
            _log.error(f"Connection error downloading {url} for job {job_id}: {e}")
            self.stats["error_connection"] += 1
        except requests.exceptions.Timeout as e:
            _log.error(f"Timeout downloading {url} for job {job_id}: {e}")
            self.stats["error_timeout"] += 1
        except IOError as e:
            _log.error(f"IO error writing file {path} for job {job_id}: {e}")
            self.stats["error_io_write"] += 1
        except Exception as e:
            _log.error(f"An unexpected error occurred downloading {url} for job {job_id}: {e}")
            self.stats["error_unexpected_download"] += 1


def main():
    parser = argparse.ArgumentParser(
        description="Download images linked in Midjourney metadata archive.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=Path.cwd() / "mj-archive",
        help="Root directory of the Midjourney metadata archive.",
    )
    parser.add_argument(
        "--job-types-to-download",
        type=str,
        default="upscale",
        help="Comma-separated list of job types to download images for (e.g., 'upscale,grid'). "
             "Provide an empty string or 'all' to download for all types found in metadata. Default: 'upscale'.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )

    archive_root_path = args.archive_root.resolve()
    if not archive_root_path.is_dir():
        _log.error(f"Archive root directory not found or is not a directory: {archive_root_path}")
        return 1

    job_types_str = args.job_types_to_download.lower()
    if job_types_str == "" or job_types_str == "all":
        job_types_set = set() # Empty set means download all
        _log.info("Will download images for all job types with image_paths.")
    else:
        job_types_set = {jt.strip() for jt in job_types_str.split(',') if jt.strip()}
        _log.info(f"Will download images for job types: {job_types_set}")


    downloader = MidjourneyDownloader(job_types_to_download=job_types_set)
    exit_code = 0
    try:
        downloader.walk_archive(archive_root=archive_root_path)
    except KeyboardInterrupt:
        _log.info("Caught KeyboardInterrupt. Exiting.")
    except Exception as e:
        _log.error(f"An unexpected error occurred during archive walk: {e}", exc_info=True)
        exit_code = 1
    finally:
        _log.info(f"Download process finished. Stats: {downloader.stats}")
        if downloader.stats.get("error_http",0) > 0 or \
           downloader.stats.get("error_connection",0) > 0 or \
           downloader.stats.get("error_timeout",0) > 0 or \
           downloader.stats.get("error_io_write",0) > 0 or \
           downloader.stats.get("error_unexpected_download",0) > 0 or \
           downloader.stats.get("error_json_decode",0) > 0 or \
           downloader.stats.get("error_file_read",0) > 0:
            exit_code = 1 # Indicate error if any download or file processing errors occurred

    return exit_code


if __name__ == "__main__":
    exit_status = main()
    exit(exit_status)
