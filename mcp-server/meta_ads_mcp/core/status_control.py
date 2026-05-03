"""Status control functionality for Meta Ads API - pause/resume campaigns, adsets, ads.

This module provides tools for managing the status of advertising objects:
- Campaigns
- Ad Sets
- Ads

Each object can be paused (status=PAUSED) or resumed (status=ACTIVE).
"""

import json
from typing import Optional
from .api import meta_api_tool, make_api_request
from .server import mcp_server
from .utils import logger


async def _update_status(
    object_id: str,
    object_type: str,
    new_status: str,
    access_token: Optional[str] = None
) -> str:
    """
    Internal helper to update status of any advertising object.

    Args:
        object_id: ID of the object (campaign, adset, or ad)
        object_type: Type name for logging ("campaign", "adset", "ad")
        new_status: New status value ("PAUSED" or "ACTIVE")
        access_token: Meta API access token

    Returns:
        JSON response string
    """
    if not object_id:
        logger.warning(f"Attempted to update {object_type} status with no ID")
        return json.dumps({"error": f"No {object_type} ID specified"}, indent=2)

    if new_status not in ("PAUSED", "ACTIVE"):
        logger.error(f"Invalid status value: {new_status}")
        return json.dumps({"error": f"Invalid status: {new_status}. Must be PAUSED or ACTIVE"}, indent=2)

    logger.info(f"Updating {object_type} {object_id} status to {new_status}")

    try:
        data = await make_api_request(
            endpoint=object_id,
            access_token=access_token,
            params={"status": new_status},
            method="POST"
        )

        if "error" in data:
            logger.error(f"Failed to update {object_type} {object_id}: {data.get('error')}")
        else:
            logger.info(f"Successfully updated {object_type} {object_id} to {new_status}")

        return json.dumps(data, indent=2)

    except Exception as e:
        logger.exception(f"Exception updating {object_type} {object_id} status")
        return json.dumps({"error": str(e)}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def pause_campaign(campaign_id: str, access_token: Optional[str] = None) -> str:
    """
    Pause a campaign by setting its status to PAUSED.

    When paused, all ads within the campaign stop delivering.
    The campaign can be resumed later with resume_campaign.

    Args:
        campaign_id: Meta Ads campaign ID
        access_token: Meta API access token (optional - will use cached token if not provided)

    Returns:
        JSON response with success status: {"success": true} or error details
    """
    return await _update_status(campaign_id, "campaign", "PAUSED", access_token)


@mcp_server.tool()
@meta_api_tool
async def resume_campaign(campaign_id: str, access_token: Optional[str] = None) -> str:
    """
    Resume a paused campaign by setting its status to ACTIVE.

    When resumed, ads within the campaign will start delivering again
    (subject to their own status and the status of their ad sets).

    Args:
        campaign_id: Meta Ads campaign ID
        access_token: Meta API access token (optional - will use cached token if not provided)

    Returns:
        JSON response with success status: {"success": true} or error details
    """
    return await _update_status(campaign_id, "campaign", "ACTIVE", access_token)


@mcp_server.tool()
@meta_api_tool
async def pause_adset(adset_id: str, access_token: Optional[str] = None) -> str:
    """
    Pause an ad set by setting its status to PAUSED.

    When paused, all ads within the ad set stop delivering.
    The ad set can be resumed later with resume_adset.

    Args:
        adset_id: Meta Ads ad set ID
        access_token: Meta API access token (optional - will use cached token if not provided)

    Returns:
        JSON response with success status: {"success": true} or error details
    """
    return await _update_status(adset_id, "adset", "PAUSED", access_token)


@mcp_server.tool()
@meta_api_tool
async def resume_adset(adset_id: str, access_token: Optional[str] = None) -> str:
    """
    Resume a paused ad set by setting its status to ACTIVE.

    When resumed, ads within the ad set will start delivering again
    (subject to their own status and the campaign's status).

    Args:
        adset_id: Meta Ads ad set ID
        access_token: Meta API access token (optional - will use cached token if not provided)

    Returns:
        JSON response with success status: {"success": true} or error details
    """
    return await _update_status(adset_id, "adset", "ACTIVE", access_token)


@mcp_server.tool()
@meta_api_tool
async def pause_ad(ad_id: str, access_token: Optional[str] = None) -> str:
    """
    Pause an ad by setting its status to PAUSED.

    When paused, the ad stops delivering immediately.
    The ad can be resumed later with resume_ad.

    Args:
        ad_id: Meta Ads ad ID
        access_token: Meta API access token (optional - will use cached token if not provided)

    Returns:
        JSON response with success status: {"success": true} or error details
    """
    return await _update_status(ad_id, "ad", "PAUSED", access_token)


@mcp_server.tool()
@meta_api_tool
async def resume_ad(ad_id: str, access_token: Optional[str] = None) -> str:
    """
    Resume a paused ad by setting its status to ACTIVE.

    When resumed, the ad will start delivering again
    (subject to its ad set's and campaign's status).

    Args:
        ad_id: Meta Ads ad ID
        access_token: Meta API access token (optional - will use cached token if not provided)

    Returns:
        JSON response with success status: {"success": true} or error details
    """
    return await _update_status(ad_id, "ad", "ACTIVE", access_token)
