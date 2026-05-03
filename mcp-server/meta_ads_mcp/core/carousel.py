"""Carousel creative functionality for Meta Ads API."""

import json
from typing import Optional, List, Dict, Any
from .api import meta_api_tool, make_api_request
from .server import mcp_server
from .utils import logger


def _build_carousel_child_attachments(
    cards: List[Dict[str, Any]],
    default_link: str
) -> List[Dict[str, Any]]:
    """
    Build child_attachments array for carousel creative.

    Args:
        cards: List of card objects with image_hash, text, and optional link
        default_link: Default link to use if card doesn't have one

    Returns:
        List of child_attachment objects
    """
    child_attachments = []

    for card in cards:
        attachment = {
            "image_hash": card["image_hash"],
            "name": card.get("text", "")[:50],  # Max 50 chars for name
            "link": card.get("link", default_link)
        }

        # Add description if provided
        if "description" in card:
            attachment["description"] = card["description"]

        child_attachments.append(attachment)

    return child_attachments


@mcp_server.tool()
@meta_api_tool
async def create_whatsapp_carousel(
    account_id: str,
    cards: List[Dict[str, Any]],
    page_id: str,
    message: str,
    client_question: str,
    access_token: Optional[str] = None,
    instagram_id: Optional[str] = None,
    whatsapp_phone: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """
    Create a WhatsApp Click-to-WhatsApp (CTWA) carousel creative.

    This creative type drives users to start a WhatsApp conversation
    with your business after clicking on the ad.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        cards: List of carousel cards. Each card should have:
            - image_hash (str): Hash of uploaded image
            - text (str): Card headline/name (max 50 chars)
            - link (str, optional): Card-specific link
        page_id: Facebook Page ID associated with the ad
        message: Primary text/caption for the ad
        client_question: Pre-filled message that user will send to WhatsApp
        access_token: Meta API access token (optional)
        instagram_id: Instagram account ID for Instagram placements
        whatsapp_phone: WhatsApp business phone number (format: +1234567890)
        name: Creative name (auto-generated if not provided)

    Returns:
        JSON response with created creative ID

    Example:
        create_whatsapp_carousel(
            account_id="act_123456789",
            cards=[
                {"image_hash": "abc123", "text": "Product 1"},
                {"image_hash": "def456", "text": "Product 2"}
            ],
            page_id="123456789",
            message="Check out our products!",
            client_question="Hi, I'm interested in your products"
        )
    """
    if not account_id:
        return json.dumps({"error": "No account ID specified"}, indent=2)

    if not cards or len(cards) < 2:
        return json.dumps({"error": "At least 2 cards required for carousel"}, indent=2)

    if len(cards) > 10:
        return json.dumps({"error": "Maximum 10 cards allowed for carousel"}, indent=2)

    if not page_id:
        return json.dumps({"error": "No page_id specified"}, indent=2)

    # Build WhatsApp link
    wa_link = "https://wa.me/"
    if whatsapp_phone:
        wa_link += whatsapp_phone.replace("+", "").replace(" ", "")

    # Build page_welcome_message with VISUAL_EDITOR format for carousel
    # Must be JSON-stringified when passed to API
    page_welcome_message = json.dumps({
        "type": "VISUAL_EDITOR",
        "version": 2,
        "landing_screen_type": "welcome_message",
        "media_type": "text",
        "text_format": {
            "customer_action_type": "autofill_message",
            "message": {
                "autofill_message": {"content": client_question},
                "text": "Здравствуйте! Чем можем помочь?"
            }
        }
    })

    # Build child attachments with CTA for each card
    child_attachments = []
    for card in cards:
        attachment = {
            "image_hash": card["image_hash"],
            "name": card.get("text", "")[:50],  # Max 50 chars for name
            "description": card.get("text", ""),
            "link": wa_link,
            "call_to_action": {
                "type": "WHATSAPP_MESSAGE",
                "value": {"app_destination": "WHATSAPP"}
            }
        }
        child_attachments.append(attachment)

    # Build object_story_spec
    object_story_spec = {
        "page_id": page_id,
        "link_data": {
            "message": message,
            "link": wa_link,
            "multi_share_optimized": True,
            "child_attachments": child_attachments,
            "call_to_action": {
                "type": "WHATSAPP_MESSAGE",
                "value": {"app_destination": "WHATSAPP"}
            },
            "page_welcome_message": page_welcome_message
        }
    }

    if instagram_id:
        object_story_spec["instagram_actor_id"] = instagram_id

    creative_name = name or f"WhatsApp Carousel - {message[:30]}"
    logger.info(f"Creating WhatsApp carousel: {creative_name} ({len(cards)} cards)")

    endpoint = f"{account_id}/adcreatives"
    params = {
        "name": creative_name,
        "object_story_spec": object_story_spec
    }

    try:
        data = await make_api_request(
            endpoint=endpoint,
            access_token=access_token,
            params=params,
            method="POST"
        )

        if "error" in data:
            logger.error(f"Failed to create WhatsApp carousel: {data.get('error')}")
        else:
            logger.info(f"Successfully created WhatsApp carousel: {data.get('id')}")

        return json.dumps(data, indent=2)

    except Exception as e:
        logger.exception(f"Exception creating WhatsApp carousel for {account_id}")
        return json.dumps({"error": str(e)}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def create_instagram_carousel(
    account_id: str,
    cards: List[Dict[str, Any]],
    page_id: str,
    instagram_id: str,
    instagram_username: str,
    message: str,
    access_token: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """
    Create an Instagram carousel creative for engagement/traffic campaigns.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        cards: List of carousel cards. Each card should have:
            - image_hash (str): Hash of uploaded image
            - text (str): Card headline/name (max 50 chars)
            - link (str, optional): Card-specific destination URL
        page_id: Facebook Page ID associated with the ad
        instagram_id: Instagram account ID
        instagram_username: Instagram username (without @)
        message: Primary text/caption for the ad
        access_token: Meta API access token (optional)
        name: Creative name (auto-generated if not provided)

    Returns:
        JSON response with created creative ID
    """
    if not account_id:
        return json.dumps({"error": "No account ID specified"}, indent=2)

    if not cards or len(cards) < 2:
        return json.dumps({"error": "At least 2 cards required for carousel"}, indent=2)

    if len(cards) > 10:
        return json.dumps({"error": "Maximum 10 cards allowed for carousel"}, indent=2)

    if not instagram_id:
        return json.dumps({"error": "No instagram_id specified"}, indent=2)

    # Default Instagram profile link
    ig_link = f"https://www.instagram.com/{instagram_username}/"

    # Build child attachments
    child_attachments = _build_carousel_child_attachments(cards, ig_link)

    # Build object_story_spec
    object_story_spec = {
        "page_id": page_id,
        "instagram_actor_id": instagram_id,
        "link_data": {
            "message": message,
            "link": ig_link,
            "child_attachments": child_attachments,
            "call_to_action": {
                "type": "LEARN_MORE"
            }
        }
    }

    creative_name = name or f"Instagram Carousel - {message[:30]}"
    logger.info(f"Creating Instagram carousel: {creative_name} ({len(cards)} cards)")

    endpoint = f"{account_id}/adcreatives"
    params = {
        "name": creative_name,
        "object_story_spec": object_story_spec
    }

    try:
        data = await make_api_request(
            endpoint=endpoint,
            access_token=access_token,
            params=params,
            method="POST"
        )

        if "error" in data:
            logger.error(f"Failed to create Instagram carousel: {data.get('error')}")
        else:
            logger.info(f"Successfully created Instagram carousel: {data.get('id')}")

        return json.dumps(data, indent=2)

    except Exception as e:
        logger.exception(f"Exception creating Instagram carousel for {account_id}")
        return json.dumps({"error": str(e)}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def create_website_carousel(
    account_id: str,
    cards: List[Dict[str, Any]],
    page_id: str,
    message: str,
    site_url: str,
    access_token: Optional[str] = None,
    instagram_id: Optional[str] = None,
    utm: Optional[str] = None,
    call_to_action: str = "LEARN_MORE",
    name: Optional[str] = None
) -> str:
    """
    Create a website traffic carousel creative.

    Drives users to your website with multiple product/service cards.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        cards: List of carousel cards. Each card should have:
            - image_hash (str): Hash of uploaded image
            - text (str): Card headline/name (max 50 chars)
            - link (str, optional): Card-specific destination URL
            - description (str, optional): Card description
        page_id: Facebook Page ID associated with the ad
        message: Primary text/caption for the ad
        site_url: Main website URL (used as default for cards without specific links)
        access_token: Meta API access token (optional)
        instagram_id: Instagram account ID for Instagram placements
        utm: UTM parameters to append to URLs (e.g., "utm_source=facebook&utm_medium=cpc")
        call_to_action: CTA button type. Options: LEARN_MORE, SHOP_NOW, SIGN_UP,
                       BOOK_TRAVEL, CONTACT_US, DOWNLOAD, GET_OFFER, etc.
        name: Creative name (auto-generated if not provided)

    Returns:
        JSON response with created creative ID
    """
    if not account_id:
        return json.dumps({"error": "No account ID specified"}, indent=2)

    if not cards or len(cards) < 2:
        return json.dumps({"error": "At least 2 cards required for carousel"}, indent=2)

    if len(cards) > 10:
        return json.dumps({"error": "Maximum 10 cards allowed for carousel"}, indent=2)

    if not site_url:
        return json.dumps({"error": "No site_url specified"}, indent=2)

    # Add UTM parameters if provided
    default_link = site_url
    if utm:
        separator = "&" if "?" in site_url else "?"
        default_link = f"{site_url}{separator}{utm}"

    # Build child attachments with UTM
    child_attachments = []
    for card in cards:
        card_link = card.get("link", default_link)
        if utm and card.get("link") and utm not in card_link:
            separator = "&" if "?" in card_link else "?"
            card_link = f"{card_link}{separator}{utm}"

        attachment = {
            "image_hash": card["image_hash"],
            "name": card.get("text", "")[:50],
            "link": card_link
        }
        if "description" in card:
            attachment["description"] = card["description"]
        child_attachments.append(attachment)

    # Build object_story_spec
    object_story_spec = {
        "page_id": page_id,
        "link_data": {
            "message": message,
            "link": default_link,
            "child_attachments": child_attachments,
            "call_to_action": {
                "type": call_to_action,
                "value": {"link": default_link}
            }
        }
    }

    if instagram_id:
        object_story_spec["instagram_actor_id"] = instagram_id

    creative_name = name or f"Website Carousel - {message[:30]}"
    logger.info(f"Creating Website carousel: {creative_name} ({len(cards)} cards, url={site_url})")

    endpoint = f"{account_id}/adcreatives"
    params = {
        "name": creative_name,
        "object_story_spec": object_story_spec
    }

    try:
        data = await make_api_request(
            endpoint=endpoint,
            access_token=access_token,
            params=params,
            method="POST"
        )

        if "error" in data:
            logger.error(f"Failed to create Website carousel: {data.get('error')}")
        else:
            logger.info(f"Successfully created Website carousel: {data.get('id')}")

        return json.dumps(data, indent=2)

    except Exception as e:
        logger.exception(f"Exception creating Website carousel for {account_id}")
        return json.dumps({"error": str(e)}, indent=2)


@mcp_server.tool()
@meta_api_tool
async def create_leadform_carousel(
    account_id: str,
    cards: List[Dict[str, Any]],
    page_id: str,
    message: str,
    lead_form_id: str,
    access_token: Optional[str] = None,
    instagram_id: Optional[str] = None,
    call_to_action: str = "SIGN_UP",
    name: Optional[str] = None
) -> str:
    """
    Create a lead generation carousel creative with instant form.

    When users click, they see a pre-filled lead form without leaving Facebook/Instagram.

    Args:
        account_id: Meta Ads account ID (format: act_XXXXXXXXX)
        cards: List of carousel cards. Each card should have:
            - image_hash (str): Hash of uploaded image
            - text (str): Card headline/name (max 50 chars)
        page_id: Facebook Page ID associated with the ad
        message: Primary text/caption for the ad
        lead_form_id: ID of the lead generation form (created in Meta Business Suite)
        access_token: Meta API access token (optional)
        instagram_id: Instagram account ID for Instagram placements
        call_to_action: CTA button type. Common for lead gen: SIGN_UP, SUBSCRIBE,
                       GET_QUOTE, LEARN_MORE, APPLY_NOW, GET_OFFER
        name: Creative name (auto-generated if not provided)

    Returns:
        JSON response with created creative ID
    """
    if not account_id:
        return json.dumps({"error": "No account ID specified"}, indent=2)

    if not cards or len(cards) < 2:
        return json.dumps({"error": "At least 2 cards required for carousel"}, indent=2)

    if len(cards) > 10:
        return json.dumps({"error": "Maximum 10 cards allowed for carousel"}, indent=2)

    if not lead_form_id:
        return json.dumps({"error": "No lead_form_id specified"}, indent=2)

    # Lead form link format
    lead_link = f"https://www.facebook.com/ads/lead_form?id={lead_form_id}"

    # Build child attachments
    child_attachments = _build_carousel_child_attachments(cards, lead_link)

    # Build object_story_spec
    object_story_spec = {
        "page_id": page_id,
        "link_data": {
            "message": message,
            "link": lead_link,
            "child_attachments": child_attachments,
            "call_to_action": {
                "type": call_to_action,
                "value": {
                    "lead_gen_form_id": lead_form_id
                }
            }
        }
    }

    if instagram_id:
        object_story_spec["instagram_actor_id"] = instagram_id

    creative_name = name or f"Lead Form Carousel - {message[:30]}"
    logger.info(f"Creating Lead Form carousel: {creative_name} ({len(cards)} cards, form={lead_form_id})")

    endpoint = f"{account_id}/adcreatives"
    params = {
        "name": creative_name,
        "object_story_spec": object_story_spec
    }

    try:
        data = await make_api_request(
            endpoint=endpoint,
            access_token=access_token,
            params=params,
            method="POST"
        )

        if "error" in data:
            logger.error(f"Failed to create Lead Form carousel: {data.get('error')}")
        else:
            logger.info(f"Successfully created Lead Form carousel: {data.get('id')}")

        return json.dumps(data, indent=2)

    except Exception as e:
        logger.exception(f"Exception creating Lead Form carousel for {account_id}")
        return json.dumps({"error": str(e)}, indent=2)
