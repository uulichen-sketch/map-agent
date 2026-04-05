from __future__ import annotations

import json
from typing import Any


def format_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_text(data: dict) -> str:
    if data.get("error"):
        return f"Error: {data.get('message', 'Unknown error')}"

    returnCode = data.get("returnCode", "")
    if returnCode and returnCode != "0":
        return f"API Error ({returnCode}): {data.get('returnDesc', 'Unknown')}"

    # Determine type by available keys
    if "sites" in data:
        return _format_sites(data)
    if "site" in data:
        return _format_single_site(data)
    if "routes" in data:
        return _format_routes(data)
    if "suggestions" in data:
        return _format_suggestions(data)

    return format_json(data)


def _format_sites(data: dict) -> str:
    total = data.get("totalCount", 0)
    lines = [f"Found {total} result(s)\n"]
    for site in data.get("sites", []):
        lines.append(f"  {site.get('name', 'Unknown')}")
        lines.append(f"    Address: {site.get('formatAddress', 'N/A')}")
        dist = site.get("distance")
        if dist is not None:
            lines.append(f"    Distance: {dist:.0f}m")
        loc = site.get("location") or {}
        if loc:
            lines.append(f"    Location: {loc.get('lng')}, {loc.get('lat')}")
        lines.append(f"    ID: {site.get('siteId', 'N/A')}")
        lines.append("")
    return "\n".join(lines)


def _format_single_site(data: dict) -> str:
    site = data.get("site") or {}
    name = site.get("name", "Unknown")
    lines = [f"  {name}"]
    addr = site.get("formatAddress")
    if addr:
        lines.append(f"    Address: {addr}")
    loc = site.get("location") or {}
    if loc:
        lines.append(f"    Location: {loc.get('lng')}, {loc.get('lat')}")
    poi = site.get("poi") or {}
    phone = poi.get("phone")
    if phone:
        lines.append(f"    Phone: {phone}")
    website = poi.get("websiteUrl")
    if website:
        lines.append(f"    Website: {website}")
    rating = poi.get("rating")
    if rating is not None:
        lines.append(f"    Rating: {rating}")
    hours = poi.get("openingHours") or {}
    texts = hours.get("texts")
    if texts:
        lines.append("    Hours:")
        for t in texts:
            lines.append(f"      {t}")
    lines.append(f"    ID: {site.get('siteId', 'N/A')}")
    return "\n".join(lines)


def _format_routes(data: dict) -> str:
    routes = data.get("routes", [])
    lines = [f"Found {len(routes)} route(s)\n"]
    for i, route in enumerate(routes, 1):
        bounds = route.get("bounds") or {}
        desc = route.get("description", "N/A")
        lines.append(f"  Route {i}: {desc}")
    return "\n".join(lines)


def _format_suggestions(data: dict) -> str:
    suggestions = data.get("suggestions", [])
    lines = [f"Found {len(suggestions)} suggestion(s)\n"]
    for s in suggestions[:10]:
        title = s.get("title", s.get("text", ""))
        lines.append(f"  - {title}")
    return "\n".join(lines)
