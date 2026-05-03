"""Video upload functionality for Meta Ads API with chunked upload support."""

import json
import os
import asyncio
from typing import Optional, Dict, Any
import httpx
from .api import META_GRAPH_API_BASE, USER_AGENT, meta_api_tool, make_api_request
from .server import mcp_server
from .utils import logger

# Constants
CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB chunks (larger = fewer requests)
SIMPLE_UPLOAD_THRESHOLD = 100 * 1024 * 1024  # 100 MB - use simple upload for most files
RETRY_ATTEMPTS = 5
INITIAL_DELAY = 1.0
START_TIMEOUT = 120.0  # 2 minutes for session init
TRANSFER_TIMEOUT = 600.0  # 10 minutes per chunk
FINISH_TIMEOUT = 120.0  # 2 minutes for finish


async def _upload_video_simple(
    account_id: str,
    access_token: str,
    file_path: str,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload video using simple upload (for files < 50MB).

    Args:
        account_id: Meta Ads account ID
        access_token: Meta API access token
        file_path: Path to video file
        title: Optional video title

    Returns:
        API response with video ID
    """
    url = f"{META_GRAPH_API_BASE}/{account_id}/advideos"
    headers = {"User-Agent": USER_AGENT}

    file_name = os.path.basename(file_path)

    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as f:
            files = {'source': (file_name, f, 'video/mp4')}
            data = {
                'access_token': access_token,
            }
            if title:
                data['title'] = title

            response = await client.post(
                url,
                data=data,
                files=files,
                headers=headers,
                timeout=600.0  # 10 minutes for upload
            )
            response.raise_for_status()
            return response.json()


async def _chunked_upload_start(
    account_id: str,
    access_token: str,
    file_size: int
) -> str:
    """
    Start chunked upload session.

    Args:
        account_id: Meta Ads account ID
        access_token: Meta API access token
        file_size: Total file size in bytes

    Returns:
        Upload session ID
    """
    url = f"{META_GRAPH_API_BASE}/{account_id}/advideos"
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            data={
                'access_token': access_token,
                'upload_phase': 'start',
                'file_size': str(file_size)
            },
            headers=headers,
            timeout=START_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        return data['upload_session_id']


async def _chunked_upload_transfer(
    account_id: str,
    access_token: str,
    session_id: str,
    file_path: str,
    file_size: int
) -> None:
    """
    Transfer file chunks.

    Args:
        account_id: Meta Ads account ID
        access_token: Meta API access token
        session_id: Upload session ID
        file_path: Path to video file
        file_size: Total file size in bytes
    """
    url = f"{META_GRAPH_API_BASE}/{account_id}/advideos"
    headers = {"User-Agent": USER_AGENT}

    start_offset = 0
    chunk_number = 0
    total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE

    with open(file_path, 'rb') as f:
        while start_offset < file_size:
            chunk_number += 1
            chunk = f.read(CHUNK_SIZE)
            end_offset = start_offset + len(chunk)

            logger.debug(f"Uploading chunk {chunk_number}/{total_chunks} "
                        f"({start_offset}-{end_offset}/{file_size})")

            # Retry logic for chunk upload
            for attempt in range(1, RETRY_ATTEMPTS + 1):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            url,
                            data={
                                'access_token': access_token,
                                'upload_phase': 'transfer',
                                'upload_session_id': session_id,
                                'start_offset': str(start_offset),
                                'video_file_chunk': chunk
                            },
                            headers=headers,
                            timeout=TRANSFER_TIMEOUT
                        )
                        response.raise_for_status()
                        data = response.json()

                        # Update start_offset from response
                        start_offset = int(data.get('start_offset', end_offset))
                        break

                except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
                    if attempt < RETRY_ATTEMPTS:
                        delay = INITIAL_DELAY * (2 ** (attempt - 1))
                        logger.warning(f"Chunk upload failed, retrying in {delay}s "
                                      f"(attempt {attempt}/{RETRY_ATTEMPTS})")
                        await asyncio.sleep(delay)
                    else:
                        raise


async def _chunked_upload_finish(
    account_id: str,
    access_token: str,
    session_id: str,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Finish chunked upload session.

    Args:
        account_id: Meta Ads account ID
        access_token: Meta API access token
        session_id: Upload session ID
        title: Optional video title

    Returns:
        API response with video ID
    """
    url = f"{META_GRAPH_API_BASE}/{account_id}/advideos"
    headers = {"User-Agent": USER_AGENT}

    data = {
        'access_token': access_token,
        'upload_phase': 'finish',
        'upload_session_id': session_id
    }

    if title:
        data['title'] = title

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            data=data,
            headers=headers,
            timeout=FINISH_TIMEOUT
        )
        response.raise_for_status()
        return response.json()


async def _upload_video_chunked(
    account_id: str,
    access_token: str,
    file_path: str,
    file_size: int,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload video using chunked upload protocol (for files >= 50MB).

    3-phase protocol:
    1. START - Initialize upload session
    2. TRANSFER - Upload chunks
    3. FINISH - Complete upload

    Args:
        account_id: Meta Ads account ID
        access_token: Meta API access token
        file_path: Path to video file
        file_size: File size in bytes
        title: Optional video title

    Returns:
        API response with video ID
    """
    logger.info(f"Starting chunked upload for {file_path} ({file_size / 1024 / 1024:.1f} MB)")

    # Phase 1: START
    logger.debug("Phase 1: Starting upload session")
    session_id = await _chunked_upload_start(account_id, access_token, file_size)
    logger.debug(f"Upload session created: {session_id}")

    # Phase 2: TRANSFER
    logger.debug("Phase 2: Transferring chunks")
    await _chunked_upload_transfer(
        account_id, access_token, session_id, file_path, file_size
    )
    logger.debug("All chunks transferred")

    # Phase 3: FINISH
    logger.debug("Phase 3: Finishing upload")
    result = await _chunked_upload_finish(account_id, access_token, session_id, title)
    logger.info(f"Chunked upload complete: video_id={result.get('id')}")

    return result


@mcp_server.tool()
@meta_api_tool
async def upload_video(
    account_id: str,
    file_path: str,
    access_token: Optional[str] = None,
    title: Optional[str] = None
) -> str:
    """
    Upload a video to Meta Ads for use in ad creatives.

    Automatically uses chunked upload for files >= 50MB, simple upload for smaller files.
    Supports videos up to 4GB.

    After upload, the video will be processed (encoded) by Meta. Use get_video_status
    to check when processing is complete before using in ads.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        file_path: Absolute path to the video file on disk
        access_token: Meta API access token (optional - will use cached token if not provided)
        title: Optional title for the video

    Returns:
        JSON response with:
        - id: Video ID to use in creatives
        - upload_method: "simple" or "chunked"

    Supported formats: MP4, MOV, AVI, MKV, WEBM
    Recommended: MP4 with H.264 codec

    Example:
        upload_video(
            account_id="act_123456789",
            file_path="/path/to/video.mp4",
            title="My Product Ad"
        )
    """
    if not account_id:
        return json.dumps({"error": "No account ID specified"}, indent=2)

    if not file_path:
        return json.dumps({"error": "No file_path specified"}, indent=2)

    # Check file exists
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"}, indent=2)

    # Get file size
    file_size = os.path.getsize(file_path)

    if file_size == 0:
        return json.dumps({"error": "File is empty"}, indent=2)

    # Max 4GB
    if file_size > 4 * 1024 * 1024 * 1024:
        return json.dumps({"error": "File too large. Maximum size is 4GB"}, indent=2)

    try:
        if file_size < SIMPLE_UPLOAD_THRESHOLD:
            # Simple upload for files < 50MB
            logger.info(f"Using simple upload for {file_path} ({file_size / 1024 / 1024:.1f} MB)")
            result = await _upload_video_simple(account_id, access_token, file_path, title)
            result["upload_method"] = "simple"
        else:
            # Chunked upload for files >= 50MB
            result = await _upload_video_chunked(
                account_id, access_token, file_path, file_size, title
            )
            result["upload_method"] = "chunked"

        result["file_size_mb"] = round(file_size / 1024 / 1024, 2)
        return json.dumps(result, indent=2)

    except httpx.HTTPStatusError as e:
        error_info = {}
        try:
            error_info = e.response.json()
        except:
            error_info = {"status_code": e.response.status_code, "text": e.response.text}

        return json.dumps({
            "error": "Video upload failed",
            "details": error_info
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_video_status(
    video_id: str,
    access_token: Optional[str] = None
) -> str:
    """
    Get the processing status of an uploaded video.

    After uploading, Meta processes (encodes) the video. This can take
    several minutes depending on video length and resolution.

    A video must be fully processed before it can be used in ad creatives.

    Args:
        video_id: Meta video ID (returned from upload_video)
        access_token: Meta API access token (optional)

    Returns:
        JSON response with:
        - id: Video ID
        - status: Processing status object containing:
            - video_status: "ready", "processing", "error"
            - processing_progress: 0-100 percentage
        - title: Video title
        - length: Duration in seconds
        - source: Video source URL (when ready)

    Status values:
        - "processing": Video is being encoded
        - "ready": Video is ready to use in ads
        - "error": Processing failed

    Example:
        get_video_status(video_id="123456789")
    """
    if not video_id:
        return json.dumps({"error": "No video_id specified"}, indent=2)

    data = await make_api_request(
        endpoint=video_id,
        access_token=access_token,
        params={
            "fields": "id,title,length,source,status,thumbnails,created_time,updated_time"
        },
        method="GET"
    )

    return json.dumps(data, indent=2)
