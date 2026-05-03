"""Audience management functionality for Meta Ads API - Lookalike audiences."""

import json
from typing import Optional
from datetime import datetime
from .api import meta_api_tool, make_api_request
from .server import mcp_server
from .utils import logger


@mcp_server.tool()
@meta_api_tool
async def create_lookalike_audience(
    account_id: str,
    seed_audience_id: str,
    country: str,
    access_token: Optional[str] = None,
    ratio: float = 0.03,
    name: Optional[str] = None
) -> str:
    """
    Create a Lookalike Audience based on a seed Custom Audience.

    Lookalike Audiences help you reach new people who are similar to your
    existing customers or engaged users.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        seed_audience_id: ID of the source Custom Audience to base the lookalike on
                         (e.g., Instagram Engagers, Website Visitors, Customer List)
        country: Country code for the lookalike audience (e.g., 'US', 'KZ', 'RU', 'GB')
        access_token: Meta API access token (optional - will use cached token if not provided)
        ratio: Size of the lookalike audience as a percentage of the country's population.
               Valid range: 0.01 to 0.10 (1% to 10%). Default: 0.03 (3%)
               Smaller ratios = more similar to seed, larger = broader reach
        name: Optional custom name for the audience. If not provided, will auto-generate
              a name like "LAL 3% US - 2024-01-15"

    Returns:
        JSON response with the created audience ID and details

    Example:
        create_lookalike_audience(
            account_id="act_123456789",
            seed_audience_id="23842588888640185",
            country="US",
            ratio=0.03
        )
    """
    if not account_id:
        return json.dumps({"error": "No account ID specified"}, indent=2)

    if not seed_audience_id:
        return json.dumps({"error": "No seed audience ID specified"}, indent=2)

    if not country:
        return json.dumps({"error": "No country specified"}, indent=2)

    # Validate ratio
    if ratio < 0.01 or ratio > 0.10:
        return json.dumps({
            "error": f"Invalid ratio {ratio}. Must be between 0.01 (1%) and 0.10 (10%)"
        }, indent=2)

    # Generate name if not provided
    if not name:
        percentage = int(ratio * 100)
        timestamp = datetime.now().strftime("%Y-%m-%d")
        name = f"LAL {percentage}% {country.upper()} - {timestamp}"

    # Build lookalike spec
    lookalike_spec = {
        "country": country.upper(),
        "ratio": ratio
    }

    logger.info(f"Creating LAL audience: {name} (seed={seed_audience_id}, country={country}, ratio={ratio})")

    endpoint = f"{account_id}/customaudiences"
    params = {
        "name": name,
        "subtype": "LOOKALIKE",
        "origin_audience_id": seed_audience_id,
        "lookalike_spec": lookalike_spec
    }

    try:
        data = await make_api_request(
            endpoint=endpoint,
            access_token=access_token,
            params=params,
            method="POST"
        )

        if "error" in data:
            logger.error(f"Failed to create LAL audience: {data.get('error')}")
        else:
            logger.info(f"Successfully created LAL audience: {data.get('id')}")

        return json.dumps(data, indent=2)

    except Exception as e:
        logger.exception(f"Exception creating LAL audience for {account_id}")
        return json.dumps({"error": str(e)}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def get_custom_audiences(
    account_id: str,
    access_token: Optional[str] = None,
    limit: int = 25
) -> str:
    """
    Get list of Custom Audiences for an ad account.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        access_token: Meta API access token (optional - will use cached token if not provided)
        limit: Maximum number of audiences to return (default: 25)

    Returns:
        JSON response with list of custom audiences including id, name, subtype,
        approximate_count (audience size), and delivery_status
    """
    if not account_id:
        logger.warning("Attempted to get custom audiences with no account ID")
        return json.dumps({"error": "No account ID specified"}, indent=2)

    logger.info(f"Fetching custom audiences for {account_id} (limit={limit})")

    endpoint = f"{account_id}/customaudiences"
    params = {
        "fields": "id,name,subtype,approximate_count,delivery_status,description,time_created,time_updated",
        "limit": limit
    }

    try:
        data = await make_api_request(
            endpoint=endpoint,
            access_token=access_token,
            params=params,
            method="GET"
        )

        if "error" in data:
            logger.error(f"Failed to get custom audiences: {data.get('error')}")
        else:
            audience_count = len(data.get("data", []))
            logger.info(f"Retrieved {audience_count} custom audiences for {account_id}")

        return json.dumps(data, indent=2)

    except Exception as e:
        logger.exception(f"Exception fetching custom audiences for {account_id}")
        return json.dumps({"error": str(e)}, indent=2)
