# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CLI argument parsing using `argparse` for both Python scripts
- Environment variable support for credentials (`MIDJOURNEY_USER_ID`, `MIDJOURNEY_SESSION_TOKEN`)
- Incremental archiving capability - can fetch from the latest date in existing archive
- Job type filtering - can specify which job types to archive and download
- Configurable JSON indentation for metadata files
- Option to overwrite existing metadata files
- Enhanced error handling with retries and timeout support
- Improved logging throughout both scripts
- Interactive shell script (`mj-download.sh`) with:
  - Python and dependency checks
  - Environment variable detection
  - Parameter customization
  - Better user guidance

### Changed
- Major refactor of `mj-metadata-archiver.py`:
  - Now supports multiple job types (not just "upscale")
  - Better API error handling
  - More flexible date handling
  - Configurable archive location
- Major refactor of `mj-downloader.py`:
  - Added job type filtering
  - Improved error handling for JSON parsing
  - Better HTTP error handling with retries
  - More robust file downloading
- Updated `README.md` with comprehensive usage instructions
- Shell script now provides clearer browser-specific instructions

### Fixed
- Missing error handling for JSON parsing
- API timeout issues
- File download interruption handling

## [0.1.0] - 2022-12-12

### Added
- Initial `PLAN.md`, `TODO.md`, `CHANGELOG.md` files
- Basic shell script `mj-download.sh` for interactive usage
- `LICENSE.txt` (MIT License)
- Updated README with installation and usage instructions

### Changed
- Improved documentation

## [0.0.1] - 2022-12-12

### Added
- Initial version of `mj-metadata-archiver.py` - crawls and archives job metadata
- Initial version of `mj-downloader.py` - downloads images from archived metadata
- Basic `requirements.txt` with requests dependency
- Initial `README.md` with basic usage instructions
