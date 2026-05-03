"""Resource handling for Meta Ads API."""

from typing import Dict, Any
import base64
from .utils import ad_creative_images


async def list_resources() -> Dict[str, Any]:
    """
    List all available resources (like ad creative images)
    
    Returns:
        Dictionary with resources list
    """
    resources = []
    
    # Add all ad creative images as resources
    for resource_id, image_info in ad_creative_images.items():
        resources.append({
            "uri": f"meta-ads://images/{resource_id}",
            "mimeType": image_info["mime_type"],
            "name": image_info["name"]
        })
    
    return {"resources": resources}


async def get_resource(resource_id: str) -> Dict[str, Any]:
    """
    Get a specific resource by URI
    
    Args:
        resource_id: Unique identifier for the resource
        
    Returns:
        Dictionary with resource data
    """
    if resource_id in ad_creative_images:
        image_info = ad_creative_images[resource_id]
        return {
            "data": base64.b64encode(image_info["data"]).decode("utf-8"),
            "mimeType": image_info["mime_type"]
        }
    
    # Resource not found
    return {"error": f"Resource not found: {resource_id}"} 