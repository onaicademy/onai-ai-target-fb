"""Conversions API (CAPI) functionality for Meta Ads API - send conversion events."""

import json
import hashlib
import uuid
import time
import asyncio
from typing import Optional, Dict, Any, List
import httpx
from .api import META_GRAPH_API_BASE, USER_AGENT, meta_api_tool
from .server import mcp_server
from .utils import logger

# Constants
RETRY_ATTEMPTS = 3
INITIAL_DELAY = 1.0  # seconds

# Valid event names
VALID_EVENTS = [
    "ViewContent",
    "CompleteRegistration",
    "Purchase",
    "Lead",
    "AddToCart",
    "InitiateCheckout",
    "Search",
    "AddPaymentInfo",
    "AddToWishlist",
    "Contact",
    "CustomizeProduct",
    "Donate",
    "FindLocation",
    "Schedule",
    "StartTrial",
    "SubmitApplication",
    "Subscribe"
]


def _hash_sha256(value: str) -> str:
    """
    Hash a value using SHA256 as required by Meta CAPI.

    Args:
        value: Plain text value to hash

    Returns:
        Lowercase hex SHA256 hash
    """
    if not value:
        return ""
    # Normalize: lowercase, strip whitespace
    normalized = str(value).lower().strip()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def _normalize_phone(phone: str) -> str:
    """
    Normalize phone number for hashing.
    Remove all non-digit characters, ensure proper format.

    Args:
        phone: Raw phone number

    Returns:
        Normalized phone number (digits only, with country code)
    """
    if not phone:
        return ""
    # Remove all non-digit characters
    digits = ''.join(c for c in str(phone) if c.isdigit())

    # Handle common formats
    if digits.startswith('8') and len(digits) == 11:
        # Russian/CIS format: 8XXXXXXXXXX -> 7XXXXXXXXXX
        digits = '7' + digits[1:]
    elif not digits.startswith('1') and not digits.startswith('7') and len(digits) == 10:
        # US format without country code: add 1
        digits = '1' + digits

    return digits


def _normalize_email(email: str) -> str:
    """
    Normalize email for hashing.

    Args:
        email: Raw email address

    Returns:
        Normalized email (lowercase, trimmed)
    """
    if not email:
        return ""
    return str(email).lower().strip()


def _build_user_data(
    phone: Optional[str] = None,
    email: Optional[str] = None,
    client_ip_address: Optional[str] = None,
    client_user_agent: Optional[str] = None,
    fbc: Optional[str] = None,
    fbp: Optional[str] = None,
    external_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build user_data object with hashed PII.

    Args:
        phone: User's phone number (will be hashed)
        email: User's email (will be hashed)
        client_ip_address: User's IP address
        client_user_agent: User's browser user agent
        fbc: Facebook click ID cookie
        fbp: Facebook browser ID cookie
        external_id: Your internal user ID (will be hashed)

    Returns:
        user_data dict for CAPI event
    """
    user_data = {}

    if phone:
        normalized_phone = _normalize_phone(phone)
        if normalized_phone:
            user_data["ph"] = [_hash_sha256(normalized_phone)]

    if email:
        normalized_email = _normalize_email(email)
        if normalized_email:
            user_data["em"] = [_hash_sha256(normalized_email)]

    if client_ip_address:
        user_data["client_ip_address"] = client_ip_address

    if client_user_agent:
        user_data["client_user_agent"] = client_user_agent

    if fbc:
        user_data["fbc"] = fbc

    if fbp:
        user_data["fbp"] = fbp

    if external_id:
        user_data["external_id"] = [_hash_sha256(str(external_id))]

    return user_data


async def _send_event_with_retry(
    pixel_id: str,
    access_token: str,
    event_data: Dict[str, Any],
    attempt: int = 1
) -> Dict[str, Any]:
    """
    Send CAPI event with retry logic.

    Args:
        pixel_id: Facebook Pixel ID
        access_token: Meta API access token
        event_data: Event payload
        attempt: Current retry attempt

    Returns:
        API response
    """
    url = f"{META_GRAPH_API_BASE}/{pixel_id}/events"
    headers = {"User-Agent": USER_AGENT}

    payload = {
        "access_token": access_token,
        "data": json.dumps([event_data])
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                data=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

        except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
            if attempt < RETRY_ATTEMPTS:
                delay = INITIAL_DELAY * (2 ** (attempt - 1))
                logger.warning(f"CAPI request failed, retrying in {delay}s (attempt {attempt}/{RETRY_ATTEMPTS})")
                await asyncio.sleep(delay)
                return await _send_event_with_retry(pixel_id, access_token, event_data, attempt + 1)
            raise


@mcp_server.tool()
@meta_api_tool
async def send_capi_event(
    pixel_id: str,
    event_name: str,
    access_token: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    client_ip_address: Optional[str] = None,
    client_user_agent: Optional[str] = None,
    fbc: Optional[str] = None,
    fbp: Optional[str] = None,
    external_id: Optional[str] = None,
    event_source_url: Optional[str] = None,
    action_source: str = "website",
    custom_data: Optional[Dict[str, Any]] = None,
    event_id: Optional[str] = None
) -> str:
    """
    Send a conversion event to Meta Conversions API (CAPI).

    CAPI allows you to send web, app, and offline events directly to Meta
    for improved ad targeting and measurement. Events sent via CAPI are
    matched with events from the browser pixel for deduplication.

    At least one of phone or email is required for user matching.

    Args:
        pixel_id: Facebook Pixel ID (dataset ID)
        event_name: Standard event name. Common values:
            - ViewContent: User viewed a product/content
            - CompleteRegistration: User completed registration
            - Purchase: User made a purchase
            - Lead: User submitted a lead form
            - AddToCart: User added item to cart
            - InitiateCheckout: User started checkout
        access_token: Meta API access token (optional - will use cached token if not provided)
        phone: User's phone number (will be hashed with SHA256)
        email: User's email address (will be hashed with SHA256)
        client_ip_address: User's IP address (improves matching)
        client_user_agent: User's browser user agent (improves matching)
        fbc: Facebook click ID cookie (_fbc)
        fbp: Facebook browser ID cookie (_fbp)
        external_id: Your internal user ID (will be hashed)
        event_source_url: URL where the event occurred
        action_source: Where the event originated. Values: website, app, email,
                      phone_call, chat, physical_store, system_generated, other
        custom_data: Additional event data like currency, value, content_ids, etc.
            Example: {"currency": "USD", "value": 99.99, "content_ids": ["SKU123"]}
        event_id: Unique event ID for deduplication. If not provided, one will be generated.

    Returns:
        JSON response with events_received count and fbtrace_id

    Example:
        send_capi_event(
            pixel_id="123456789",
            event_name="Purchase",
            phone="+1234567890",
            email="user@example.com",
            custom_data={"currency": "USD", "value": 99.99}
        )
    """
    if not pixel_id:
        return json.dumps({"error": "No pixel_id specified"}, indent=2)

    if not event_name:
        return json.dumps({"error": "No event_name specified"}, indent=2)

    if event_name not in VALID_EVENTS:
        return json.dumps({
            "error": f"Invalid event_name: {event_name}",
            "valid_events": VALID_EVENTS
        }, indent=2)

    if not phone and not email:
        return json.dumps({
            "error": "At least one of phone or email is required for user matching"
        }, indent=2)

    # Build user_data with hashed PII
    user_data = _build_user_data(
        phone=phone,
        email=email,
        client_ip_address=client_ip_address,
        client_user_agent=client_user_agent,
        fbc=fbc,
        fbp=fbp,
        external_id=external_id
    )

    if not user_data:
        return json.dumps({
            "error": "Failed to build user_data - no valid identifiers provided"
        }, indent=2)

    # Generate event_id if not provided (for deduplication)
    if not event_id:
        event_id = str(uuid.uuid4())

    # Build event data
    event_data = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "event_id": event_id,
        "action_source": action_source,
        "user_data": user_data
    }

    if event_source_url:
        event_data["event_source_url"] = event_source_url

    if custom_data:
        event_data["custom_data"] = custom_data

    try:
        result = await _send_event_with_retry(pixel_id, access_token, event_data)

        # Add event_id to response for reference
        result["event_id"] = event_id

        return json.dumps(result, indent=2)

    except httpx.HTTPStatusError as e:
        error_info = {}
        try:
            error_info = e.response.json()
        except:
            error_info = {"status_code": e.response.status_code, "text": e.response.text}

        return json.dumps({
            "error": "CAPI request failed",
            "details": error_info,
            "event_id": event_id
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "event_id": event_id
        }, indent=2)
