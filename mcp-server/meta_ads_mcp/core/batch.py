"""Batch API functionality for Meta Ads API - execute multiple requests in one call."""

import json
import asyncio
from typing import Optional, List, Dict, Any
import httpx
from .api import META_GRAPH_API_BASE, USER_AGENT, meta_api_tool
from .server import mcp_server
from .utils import logger

# Constants
MAX_BATCH_SIZE = 50
RETRY_ATTEMPTS = 5
INITIAL_DELAY = 1.0  # seconds
CHUNK_DELAY = 0.5  # seconds between chunks


async def _execute_batch_chunk(
    access_token: str,
    requests: List[Dict[str, Any]],
    attempt: int = 1
) -> List[Dict[str, Any]]:
    """
    Execute a single batch chunk with retry logic.

    Args:
        access_token: Meta API access token
        requests: List of batch requests (max 50)
        attempt: Current retry attempt number

    Returns:
        List of responses for each request
    """
    url = META_GRAPH_API_BASE
    headers = {"User-Agent": USER_AGENT}

    # Prepare batch payload
    batch_payload = json.dumps(requests)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                data={
                    "access_token": access_token,
                    "batch": batch_payload
                },
                headers=headers,
                timeout=30.0
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            # Check for rate limiting
            if e.response.status_code == 429 or (
                e.response.status_code == 400 and "rate limit" in e.response.text.lower()
            ):
                if attempt < RETRY_ATTEMPTS:
                    delay = INITIAL_DELAY * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(f"Rate limited, retrying in {delay}s (attempt {attempt}/{RETRY_ATTEMPTS})")
                    await asyncio.sleep(delay)
                    return await _execute_batch_chunk(access_token, requests, attempt + 1)

            # Re-raise if not retryable or max attempts reached
            raise

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if attempt < RETRY_ATTEMPTS:
                delay = INITIAL_DELAY * (2 ** (attempt - 1))
                logger.warning(f"Connection error, retrying in {delay}s (attempt {attempt}/{RETRY_ATTEMPTS})")
                await asyncio.sleep(delay)
                return await _execute_batch_chunk(access_token, requests, attempt + 1)
            raise


def _parse_batch_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a single batch response item.

    Args:
        response: Raw response from batch API

    Returns:
        Parsed response with success flag and data/error
    """
    if response is None:
        return {"success": False, "error": "Null response"}

    code = response.get("code", 0)
    body = response.get("body", "{}")

    try:
        parsed_body = json.loads(body) if isinstance(body, str) else body
    except json.JSONDecodeError:
        parsed_body = {"raw": body}

    if 200 <= code < 300:
        return {"success": True, "data": parsed_body, "code": code}
    else:
        return {
            "success": False,
            "error": parsed_body.get("error", parsed_body),
            "code": code
        }


@mcp_server.tool()
@meta_api_tool
async def batch_request(
    access_token: str,
    requests: List[Dict[str, Any]]
) -> str:
    """
    Execute multiple Graph API requests in a single call.

    This is highly efficient for operations like:
    - Getting insights for multiple campaigns/adsets/ads
    - Updating multiple objects at once
    - Bulk reading object details

    The batch API automatically handles:
    - Splitting requests into chunks of 50 (Meta API limit)
    - Retry with exponential backoff on rate limits
    - Parsing individual responses

    Args:
        access_token: Meta API access token
        requests: List of request objects, each containing:
            - method (str): HTTP method - "GET", "POST", or "DELETE"
            - relative_url (str): API endpoint path (e.g., "123456789/insights")
            - body (str, optional): URL-encoded body for POST requests
                                   (e.g., "status=PAUSED&name=New+Name")

    Returns:
        JSON response with results array containing success/error for each request

    Example:
        batch_request(
            access_token="...",
            requests=[
                {"method": "GET", "relative_url": "act_123/campaigns?fields=id,name"},
                {"method": "GET", "relative_url": "act_123/adsets?fields=id,name"},
                {"method": "POST", "relative_url": "123456789", "body": "status=PAUSED"}
            ]
        )
    """
    if not access_token:
        return json.dumps({"error": "No access token provided"}, indent=2)

    if not requests or len(requests) == 0:
        return json.dumps({"error": "No requests provided"}, indent=2)

    # Validate requests
    for i, req in enumerate(requests):
        if "method" not in req:
            return json.dumps({"error": f"Request {i} missing 'method'"}, indent=2)
        if "relative_url" not in req:
            return json.dumps({"error": f"Request {i} missing 'relative_url'"}, indent=2)
        if req["method"] not in ["GET", "POST", "DELETE"]:
            return json.dumps({"error": f"Request {i} has invalid method: {req['method']}"}, indent=2)

    # Split into chunks of MAX_BATCH_SIZE
    chunks = [requests[i:i + MAX_BATCH_SIZE] for i in range(0, len(requests), MAX_BATCH_SIZE)]

    all_results = []
    stats = {
        "total": len(requests),
        "success": 0,
        "error": 0,
        "chunks": len(chunks)
    }

    try:
        for chunk_idx, chunk in enumerate(chunks):
            logger.debug(f"Processing batch chunk {chunk_idx + 1}/{len(chunks)} ({len(chunk)} requests)")

            # Execute chunk
            raw_responses = await _execute_batch_chunk(access_token, chunk)

            # Parse responses
            for resp in raw_responses:
                parsed = _parse_batch_response(resp)
                all_results.append(parsed)

                if parsed["success"]:
                    stats["success"] += 1
                else:
                    stats["error"] += 1

            # Delay between chunks to avoid rate limiting
            if chunk_idx < len(chunks) - 1:
                await asyncio.sleep(CHUNK_DELAY)

        return json.dumps({
            "results": all_results,
            "stats": stats
        }, indent=2)

    except httpx.HTTPStatusError as e:
        error_info = {}
        try:
            error_info = e.response.json()
        except:
            error_info = {"status_code": e.response.status_code, "text": e.response.text}

        return json.dumps({
            "error": "Batch request failed",
            "details": error_info,
            "stats": stats
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "stats": stats
        }, indent=2)
