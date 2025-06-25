#!/usr/bin/env bash

echo "Midjourney Archiver Setup"
echo "-------------------------"
echo "This script will help you download your Midjourney metadata and images."
echo

# Check for Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null
then
    echo "Error: Python is not installed or not in your PATH."
    echo "Please install Python 3.9 or newer and try again."
    exit 1
fi

# Determine Python command
PYTHON_CMD="python"
if command -v python3 &> /dev/null
then
    PYTHON_CMD="python3"
fi

# Check for requests module
if ! $PYTHON_CMD -c "import requests" &> /dev/null
then
    echo "Python module 'requests' not found."
    echo "You can install it by running: pip install requests (or pip3 install requests)"
    echo "Please install it and try again."
    # Optionally, offer to install it:
    # read -p "Would you like to try and install it now? (y/n): " INSTALL_REQUESTS
    # if [[ "$INSTALL_REQUESTS" == "y" || "$INSTALL_REQUESTS" == "Y" ]]; then
    #     $PYTHON_CMD -m pip install requests
    #     if ! $PYTHON_CMD -c "import requests" &> /dev/null; then
    #         echo "Installation failed. Please install 'requests' manually."
    #         exit 1
    #     fi
    # else
    #     exit 1
    # fi
    exit 1
fi


# Check for User ID in environment variables
if [ -n "$MIDJOURNEY_USER_ID" ]; then
    echo "Found MIDJOURNEY_USER_ID in environment variables: $MIDJOURNEY_USER_ID"
    read -p "Do you want to use this User ID? (Y/n): " use_env_user_id
    if [[ "$use_env_user_id" == "n" || "$use_env_user_id" == "N" ]]; then
        unset MIDJOURNEY_USER_ID # Unset to prompt user below
    fi
fi

# Check for Session Token in environment variables
if [ -n "$MIDJOURNEY_SESSION_TOKEN" ]; then
    echo "Found MIDJOURNEY_SESSION_TOKEN in environment variables."
    read -p "Do you want to use this Session Token? (Y/n): " use_env_session_token
    if [[ "$use_env_session_token" == "n" || "$use_env_session_token" == "N" ]]; then
        unset MIDJOURNEY_SESSION_TOKEN # Unset to prompt user below
    fi
fi

echo
echo "Instructions to get your Midjourney User ID and Session Token:"
echo "(These are generally for Chromium-based browsers like Chrome, Edge, Brave, Opera)"
echo
echo "1. Open your web browser and go to: https://www.midjourney.com/app/"
echo "2. Sign in to your Midjourney account if you haven't already."
echo "3. Open the Developer Tools. You can usually do this by pressing F12, or right-clicking"
echo "   on the page and selecting 'Inspect' or 'Inspect Element'."
echo
echo "To get your User ID:"
echo "4. In Developer Tools, go to the 'Network' tab."
echo "5. Make sure 'Fetch/XHR' is selected as a filter (if available)."
echo "6. Look for a request in the list that starts with 'recent-jobs?...' or similar."
echo "   You might need to scroll or interact with the Midjourney app (e.g., click 'Archive') to trigger this request."
echo "7. Select this request. In the 'Headers' (or 'Request') tab for this request, look at the"
echo "   'Request URL' or 'Query String Parameters'. You should see 'user_id=YOUR_USER_ID'."
echo "   It's a long string of letters and numbers."
echo
echo "To get your Session Token:"
echo "8. In Developer Tools, go to the 'Application' tab (it might be under 'More tabs' or '>>')."
echo "9. On the left side, under 'Storage', expand 'Cookies' and select 'https://www.midjourney.com'."
echo "10. In the table of cookies, find the cookie named '__Secure-next-auth.session-token'."
echo "11. Copy its entire 'Cookie Value'."
echo

# Prompt for User ID if not set from env
if [ -z "$MIDJOURNEY_USER_ID" ]; then
    read -p "Enter your Midjourney User ID: " MIDJOURNEY_USER_ID_INPUT
    export MIDJOURNEY_USER_ID=$MIDJOURNEY_USER_ID_INPUT
else
    echo "Using User ID from environment."
fi

# Prompt for Session Token if not set from env
if [ -z "$MIDJOURNEY_SESSION_TOKEN" ]; then
    read -p "Enter your Midjourney Session Token: " -e MIDJOURNEY_SESSION_TOKEN_INPUT
    export MIDJOURNEY_SESSION_TOKEN=$MIDJOURNEY_SESSION_TOKEN_INPUT
else
    echo "Using Session Token from environment."
fi

if [ -z "$MIDJOURNEY_USER_ID" ] || [ -z "$MIDJOURNEY_SESSION_TOKEN" ]; then
    echo "Error: User ID and Session Token are required."
    exit 1
fi

echo
echo "Thanks! Credentials are set."
echo "User ID: $MIDJOURNEY_USER_ID"
# For security, don't echo the session token directly, just confirm it's set.
echo "Session Token: [set]"
echo

# --- Customizable settings for the scripts ---
ARCHIVE_ROOT_DIR="./mj-archive"
METADATA_PAGE_LIMIT="" # Empty means no limit for metadata archiver
METADATA_JOB_TYPE="upscale" # "upscale", "grid", "all", "None"
METADATA_FROM_DATE="" # e.g. "2023-01-01"
METADATA_GET_FROM_ARCHIVE="true" # "true" or "false"
METADATA_OVERWRITE="false" # "true" or "false"
DOWNLOADER_JOB_TYPES="upscale" # "upscale,grid", or "all" or empty for all
LOG_LEVEL="INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL

echo "Default settings for scripts:"
echo "Archive Root: $ARCHIVE_ROOT_DIR"
echo "Metadata - Page Limit: ${METADATA_PAGE_LIMIT:-Not set (all pages)}"
echo "Metadata - Job Type: $METADATA_JOB_TYPE"
echo "Metadata - From Date: ${METADATA_FROM_DATE:-Not set (newest)}"
echo "Metadata - Get From Date From Archive: $METADATA_GET_FROM_ARCHIVE"
echo "Metadata - Overwrite Existing: $METADATA_OVERWRITE"
echo "Downloader - Job Types: $DOWNLOADER_JOB_TYPES"
echo "Log Level: $LOG_LEVEL"
echo
read -p "Do you want to customize these settings? (y/N): " customize_settings

if [[ "$customize_settings" == "y" || "$customize_settings" == "Y" ]]; then
    read -p "Enter Archive Root Directory [$ARCHIVE_ROOT_DIR]: " temp_archive_root && ARCHIVE_ROOT_DIR=${temp_archive_root:-$ARCHIVE_ROOT_DIR}
    read -p "Metadata - Page Limit (number, empty for no limit) [$METADATA_PAGE_LIMIT]: " temp_page_limit && METADATA_PAGE_LIMIT=${temp_page_limit:-$METADATA_PAGE_LIMIT}
    read -p "Metadata - Job Type (upscale, grid, all) [$METADATA_JOB_TYPE]: " temp_job_type && METADATA_JOB_TYPE=${temp_job_type:-$METADATA_JOB_TYPE}
    read -p "Metadata - From Date (YYYY-MM-DD, empty for newest) [$METADATA_FROM_DATE]: " temp_from_date && METADATA_FROM_DATE=${temp_from_date:-$METADATA_FROM_DATE}
    read -p "Metadata - Get From Date From Archive (true/false) [$METADATA_GET_FROM_ARCHIVE]: " temp_get_from_archive && METADATA_GET_FROM_ARCHIVE=${temp_get_from_archive:-$METADATA_GET_FROM_ARCHIVE}
    read -p "Metadata - Overwrite Existing (true/false) [$METADATA_OVERWRITE]: " temp_overwrite && METADATA_OVERWRITE=${temp_overwrite:-$METADATA_OVERWRITE}
    read -p "Downloader - Job Types to Download (e.g., upscale,grid or all) [$DOWNLOADER_JOB_TYPES]: " temp_downloader_types && DOWNLOADER_JOB_TYPES=${temp_downloader_types:-$DOWNLOADER_JOB_TYPES}
    read -p "Log Level (DEBUG, INFO, WARNING, ERROR) [$LOG_LEVEL]: " temp_log_level && LOG_LEVEL=${temp_log_level:-$LOG_LEVEL}
fi

# Construct arguments for mj-metadata-archiver.py
METADATA_ARGS=()
METADATA_ARGS+=("--archive-root" "$ARCHIVE_ROOT_DIR")
METADATA_ARGS+=("--log-level" "$LOG_LEVEL")
if [ -n "$METADATA_PAGE_LIMIT" ]; then METADATA_ARGS+=("--page-limit" "$METADATA_PAGE_LIMIT"); fi
if [ -n "$METADATA_JOB_TYPE" ]; then METADATA_ARGS+=("--job-type" "$METADATA_JOB_TYPE"); fi
if [ -n "$METADATA_FROM_DATE" ]; then METADATA_ARGS+=("--from-date" "$METADATA_FROM_DATE"); fi
if [[ "$METADATA_GET_FROM_ARCHIVE" == "true" ]]; then METADATA_ARGS+=("--get-from-date-from-archive"); fi
if [[ "$METADATA_OVERWRITE" == "true" ]]; then METADATA_ARGS+=("--overwrite-metadata"); fi

# Construct arguments for mj-downloader.py
DOWNLOADER_ARGS=()
DOWNLOADER_ARGS+=("--archive-root" "$ARCHIVE_ROOT_DIR")
DOWNLOADER_ARGS+=("--log-level" "$LOG_LEVEL")
if [ -n "$DOWNLOADER_JOB_TYPES" ]; then DOWNLOADER_ARGS+=("--job-types-to-download" "$DOWNLOADER_JOB_TYPES"); fi


echo
echo "Starting metadata archiving..."
echo "Command: $PYTHON_CMD ./mj-metadata-archiver.py ${METADATA_ARGS[@]}"
$PYTHON_CMD ./mj-metadata-archiver.py "${METADATA_ARGS[@]}"
ARCHIVER_EXIT_CODE=$?

if [ $ARCHIVER_EXIT_CODE -ne 0 ]; then
    echo "Metadata archiver finished with errors (exit code $ARCHIVER_EXIT_CODE)."
    read -p "Do you want to continue to the downloader despite metadata errors? (y/N): " continue_anyway
    if [[ "$continue_anyway" != "y" && "$continue_anyway" != "Y" ]]; then
        echo "Exiting."
        exit $ARCHIVER_EXIT_CODE
    fi
else
    echo "Metadata archiving completed."
fi

echo
echo "Starting image downloading..."
echo "Command: $PYTHON_CMD ./mj-downloader.py ${DOWNLOADER_ARGS[@]}"
$PYTHON_CMD ./mj-downloader.py "${DOWNLOADER_ARGS[@]}"
DOWNLOADER_EXIT_CODE=$?

if [ $DOWNLOADER_EXIT_CODE -ne 0 ]; then
    echo "Downloader finished with errors (exit code $DOWNLOADER_EXIT_CODE)."
else
    echo "Image downloading completed."
fi

echo
echo "All done!"
if [ $ARCHIVER_EXIT_CODE -ne 0 ] || [ $DOWNLOADER_EXIT_CODE -ne 0 ]; then
    echo "There were errors during the process. Please check the logs above."
    exit 1
else
    echo "Process completed successfully."
    exit 0
fi
