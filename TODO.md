# TODO

## Immediate Priority (Week 1-2)

### Project Structure
- [ ] Create proper Python package structure under `src/midjourney_archiver/`
- [ ] Split monolithic scripts into modules (api, core, cli, storage)
- [ ] Create `__init__.py` files for all packages
- [ ] Move existing scripts to legacy folder for reference

### Code Quality
- [ ] Add type hints to all functions in `mj-metadata-archiver.py`
- [ ] Add type hints to all functions in `mj-downloader.py`
- [ ] Replace os.path with pathlib throughout codebase
- [ ] Add docstrings to all classes and functions
- [ ] Create custom exception classes for better error handling
- [ ] Implement proper logging with configurable levels

### Configuration System
- [ ] Create `config.py` module for configuration management
- [ ] Implement YAML-based configuration file support
- [ ] Add configuration schema validation
- [ ] Support config hierarchy (defaults → system → user → project → env → CLI)
- [ ] Create example configuration file

### Testing Infrastructure
- [ ] Set up pytest framework
- [ ] Create initial unit tests for core functions
- [ ] Add GitHub Actions workflow for automated testing
- [ ] Configure mypy for type checking
- [ ] Set up pre-commit hooks

## Short Term Priority (Week 3-4)

### API Client Refactoring
- [ ] Create dedicated `api/client.py` module
- [ ] Implement session management class
- [ ] Add connection pooling
- [ ] Implement retry logic with exponential backoff
- [ ] Add rate limiting to prevent API throttling
- [ ] Create Pydantic models for API responses

### Enhanced CLI
- [ ] Migrate from argparse to Click framework
- [ ] Implement subcommand structure (auth, archive, download, search, etc.)
- [ ] Add interactive prompts for missing parameters
- [ ] Implement progress bars with rich/tqdm
- [ ] Add shell completion support
- [ ] Create `--help` with examples for all commands

### Error Handling
- [ ] Implement comprehensive try-except blocks
- [ ] Add specific error messages with suggestions
- [ ] Create error recovery mechanisms
- [ ] Add validation for all inputs
- [ ] Implement graceful shutdown handling

### Documentation
- [ ] Update README.md with new package structure
- [ ] Create detailed installation guide
- [ ] Document all CLI commands with examples
- [ ] Add troubleshooting guide
- [ ] Create developer documentation

## Medium Term Priority (Month 2-3)

### Performance Improvements
- [ ] Implement concurrent image downloading
- [ ] Add async/await support for API calls
- [ ] Create download queue management system
- [ ] Implement resume capability for interrupted downloads
- [ ] Add progress tracking for batch operations
- [ ] Optimize file I/O operations

### Database Integration
- [ ] Design SQLite schema for metadata storage
- [ ] Implement database initialization and migration
- [ ] Create indexing for fast searches
- [ ] Add full-text search on prompts
- [ ] Implement query interface
- [ ] Add export functionality (CSV, JSON)

### Packaging and Distribution
- [ ] Create `pyproject.toml` for modern Python packaging
- [ ] Set up setuptools configuration
- [ ] Create entry points for CLI commands
- [ ] Build and test wheel distribution
- [ ] Prepare for PyPI publication
- [ ] Create GitHub release automation

### Security Enhancements
- [ ] Integrate keyring for secure credential storage
- [ ] Add credential encryption options
- [ ] Implement secure deletion of sensitive data
- [ ] Add input sanitization
- [ ] Create security documentation

## Long Term Priority (Month 4-6)

### Advanced Features
- [ ] Implement duplicate detection using content hashing
- [ ] Add image format conversion options
- [ ] Create thumbnail generation
- [ ] Implement EXIF metadata embedding
- [ ] Add archive verification commands
- [ ] Create HTML gallery export

### Automation
- [ ] Add cron job examples for scheduled archiving
- [ ] Implement webhook notifications
- [ ] Create Docker container
- [ ] Add docker-compose configuration
- [ ] Create systemd service files
- [ ] Add Windows Task Scheduler integration

### Cloud Storage Support
- [ ] Add S3 backend support
- [ ] Implement Google Cloud Storage integration
- [ ] Add Azure Blob Storage support
- [ ] Create abstraction layer for storage backends
- [ ] Add sync functionality between local and cloud

### Web Interface (Optional)
- [ ] Design RESTful API for web access
- [ ] Create basic Flask/FastAPI application
- [ ] Implement gallery view
- [ ] Add search functionality
- [ ] Create download management interface
- [ ] Add real-time progress updates

## Continuous Tasks

### Code Quality
- [ ] Maintain > 80% test coverage
- [ ] Regular dependency updates
- [ ] Code review all changes
- [ ] Update documentation with changes
- [ ] Monitor and fix security vulnerabilities

### Community
- [ ] Respond to GitHub issues
- [ ] Review and merge pull requests
- [ ] Create contributing guidelines
- [ ] Build example scripts and tutorials
- [ ] Maintain changelog

## Bug Fixes and Improvements

### Known Issues
- [ ] Fix hard-coded limit of 10 in main() function
- [ ] Handle malformed JSON responses gracefully
- [ ] Improve error messages for authentication failures
- [ ] Fix potential path traversal vulnerabilities
- [ ] Handle network interruptions during download

### User Experience
- [ ] Add verbose mode for debugging
- [ ] Implement quiet mode for automation
- [ ] Add dry-run option for testing
- [ ] Create interactive setup wizard
- [ ] Add command aliases for common operations

## Notes
- Prioritize backward compatibility during refactoring
- Keep legacy scripts functional until new version is stable
- Focus on user experience and ease of installation
- Ensure cross-platform compatibility (Windows, macOS, Linux)
- Consider user feedback and feature requests from GitHub issues