from __future__ import annotations

import json
import os
import re
import tempfile
from copy import deepcopy
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(os.environ.get("ISH_SOURCE_ROOT", Path(__file__).resolve().parents[1])).resolve()
CONTENT_ROOT = ROOT / "content"
ROUTE_PATTERN = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*/?)+$")
IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
RESERVED_ROUTE_PARTS = {"assets", "content", "editor", "scripts", ".git", ".github"}

COLLECTION_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "awards": ("id", "award", "year", "recipient"),
    "board": ("id", "name", "image"),
    "committees": ("id", "name", "group", "image"),
    "communications": ("id", "title", "url"),
    "former_meetings": ("id", "number", "year", "location"),
    "location_carousel": ("id", "title", "image", "alt"),
    "speakers": ("id", "name", "image"),
    "sponsors": ("id", "group", "name", "image"),
    "travel_links": ("id", "label", "url"),
}

COLLECTION_LABELS = {
    "awards": "Premios",
    "board": "Consejo asesor",
    "committees": "Comites",
    "communications": "Comunicaciones",
    "former_meetings": "Reuniones anteriores",
    "location_carousel": "Carrusel de destino",
    "speakers": "Conferencistas",
    "sponsors": "Socios y auspiciadores",
    "travel_links": "Enlaces para el viaje",
}

FIELD_LABELS = {
    "award": "premio",
    "id": "identificador",
    "name": "nombre",
    "recipient": "persona premiada",
    "group": "grupo",
    "image": "imagen",
    "title": "titulo",
    "url": "enlace",
    "number": "numero",
    "year": "ano",
    "location": "ubicacion",
    "alt": "texto alternativo",
    "label": "etiqueta",
}

ALLOWED_RICH_TAGS = {
    "p",
    "br",
    "strong",
    "em",
    "a",
    "ul",
    "ol",
    "li",
    "h2",
    "h3",
    "blockquote",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "caption",
    "hr",
}
VOID_TAGS = {"br", "hr"}


class ContentValidationError(ValueError):
    pass


def _has_content(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def collection_item_complete(collection: str, item: Any) -> bool:
    requirements = COLLECTION_REQUIREMENTS.get(collection)
    if requirements is None:
        return isinstance(item, dict)
    return isinstance(item, dict) and all(_has_content(item.get(field)) for field in requirements)


def normalize_content_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    collections = bundle.get("collections")
    if not isinstance(collections, dict):
        return bundle
    communications = collections.get("communications", [])
    if isinstance(communications, list):
        for item in communications:
            if not isinstance(item, dict):
                continue
            item.setdefault("published", True)
            item.setdefault("image", "")
            item.setdefault("image_alt", "")
            item.setdefault("body_html", "")
            if not _has_content(item.get("title")) or not _has_content(item.get("url")):
                item["published"] = False
    return bundle


def validate_publishable_content(bundle: dict[str, Any]) -> None:
    validate_content_bundle(bundle)
    problems: list[str] = []
    collections = bundle["collections"]
    for collection, requirements in COLLECTION_REQUIREMENTS.items():
        seen_ids: set[str] = set()
        for index, item in enumerate(collections.get(collection, []), start=1):
            label = COLLECTION_LABELS.get(collection, collection)
            if not isinstance(item, dict):
                problems.append(f"{label}, registro {index}: el registro no es valido.")
                continue
            item_requirements = ("id",) if collection == "communications" and item.get("published") is False else requirements
            missing = [FIELD_LABELS.get(field, field) for field in item_requirements if not _has_content(item.get(field))]
            item_id = str(item.get("id", "")).strip()
            if item_id and (not IDENTIFIER_PATTERN.fullmatch(item_id) or item_id in seen_ids):
                missing.append("identificador valido y unico")
            if item_id:
                seen_ids.add(item_id)
            if missing:
                problems.append(f'{label}, registro {index}: completa {", ".join(missing)}.')
    if problems:
        raise ContentValidationError("No se puede publicar contenido incompleto. " + " ".join(problems[:6]))


def _safe_href(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme and parsed.scheme not in {"http", "https", "mailto", "tel"}:
        return ""
    if value.lower().startswith(("javascript:", "data:")):
        return ""
    return value


class _RichHTMLSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.output: list[str] = []
        self.open_tags: list[str] = []
        self.suppressed_tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "iframe", "object", "embed"}:
            self.suppressed_tags.append(tag)
            return
        if self.suppressed_tags:
            return
        if tag not in ALLOWED_RICH_TAGS:
            return
        clean_attrs: list[str] = []
        attr_map = {name.lower(): value or "" for name, value in attrs}
        if tag == "a":
            href = _safe_href(attr_map.get("href", ""))
            if href:
                clean_attrs.append(f'href="{escape(href, quote=True)}"')
                if href.startswith(("http://", "https://")):
                    clean_attrs.extend(['target="_blank"', 'rel="noreferrer"'])
        if tag in {"th", "td"}:
            colspan = attr_map.get("colspan", "")
            rowspan = attr_map.get("rowspan", "")
            if colspan.isdigit() and 1 <= int(colspan) <= 12:
                clean_attrs.append(f'colspan="{colspan}"')
            if rowspan.isdigit() and 1 <= int(rowspan) <= 50:
                clean_attrs.append(f'rowspan="{rowspan}"')
            if tag == "th" and attr_map.get("scope") in {"row", "col"}:
                clean_attrs.append(f'scope="{attr_map["scope"]}"')
        attrs_html = f" {' '.join(clean_attrs)}" if clean_attrs else ""
        self.output.append(f"<{tag}{attrs_html}>")
        if tag not in VOID_TAGS:
            self.open_tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.suppressed_tags:
            if tag == self.suppressed_tags[-1]:
                self.suppressed_tags.pop()
            return
        if tag not in ALLOWED_RICH_TAGS or tag in VOID_TAGS:
            return
        if tag not in self.open_tags:
            return
        while self.open_tags:
            current = self.open_tags.pop()
            self.output.append(f"</{current}>")
            if current == tag:
                break

    def handle_data(self, data: str) -> None:
        if not self.suppressed_tags:
            self.output.append(escape(data))

    def close(self) -> None:
        super().close()
        while self.open_tags:
            self.output.append(f"</{self.open_tags.pop()}>")


def sanitize_rich_html(value: str) -> str:
    parser = _RichHTMLSanitizer()
    parser.feed(value)
    parser.close()
    return "".join(parser.output).strip()


def normalize_route(route: str) -> str:
    normalized = route.strip().strip("/")
    if not normalized:
        return ""
    if not ROUTE_PATTERN.fullmatch(normalized):
        raise ContentValidationError(
            f"Invalid route '{route}'. Use lowercase letters, numbers and hyphens."
        )
    parts = normalized.split("/")
    if len(parts) > 3:
        raise ContentValidationError(f"Route '{route}' is more than three levels deep.")
    if any(part in RESERVED_ROUTE_PARTS for part in parts):
        raise ContentValidationError(f"Route '{route}' uses a reserved path.")
    return normalized


def _validate_href(value: str, location: str) -> None:
    if not value:
        return
    if _safe_href(value) != value.strip():
        raise ContentValidationError(f"Unsafe link in {location}.")
    parsed = urlparse(value)
    if not parsed.scheme:
        path = parsed.path.replace("\\", "/")
        if any(part == ".." for part in path.split("/")):
            raise ContentValidationError(f"Link in {location} leaves the site root.")


def _validate_references(
    value: Any,
    *,
    page_ids: set[str],
    site_links: set[str],
    location: str,
) -> None:
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_references(
                item,
                page_ids=page_ids,
                site_links=site_links,
                location=f"{location}[{index}]",
            )
        return
    if not isinstance(value, dict):
        return
    for key, item in value.items():
        item_location = f"{location}.{key}"
        if key in {"focal_x", "focal_y"} and (not isinstance(item, (int, float)) or isinstance(item, bool) or not 0 <= item <= 100):
            raise ContentValidationError(f"Image focal point in {item_location} must be between 0 and 100.")
        if key in {"page_id", "panel_link_page_id"} and item:
            if not isinstance(item, str) or item not in page_ids:
                raise ContentValidationError(f"Unknown page reference '{item}' in {item_location}.")
        if key == "site_link" and item:
            if not isinstance(item, str) or item not in site_links:
                raise ContentValidationError(f"Unknown shared link '{item}' in {item_location}.")
        if (key in {"url", "href", "map_url", "abstract_url", "report_url", "public_url"} or key.endswith("_url")) and isinstance(item, str):
            _validate_href(item, item_location)
        _validate_references(
            item,
            page_ids=page_ids,
            site_links=site_links,
            location=item_location,
        )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContentValidationError(f"Unable to read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContentValidationError(f"{path} must contain a JSON object.")
    return payload


def load_content_bundle(
    content_root: Path | None = None,
    override_path: Path | None = None,
) -> dict[str, Any]:
    env_override = os.environ.get("ISH_CONTENT_BUNDLE")
    if override_path is None and env_override:
        override_path = Path(env_override)
    if override_path is not None:
        bundle = _read_json(override_path)
        normalize_content_bundle(bundle)
        validate_content_bundle(bundle)
        return bundle

    root = content_root or CONTENT_ROOT
    site = _read_json(root / "site.json")
    collections: dict[str, Any] = {}
    for path in sorted((root / "collections").glob("*.json")):
        collections[path.stem] = _read_json(path).get("items", [])
    pages = [_read_json(path) for path in sorted((root / "pages").glob("*.json"))]
    bundle = {
        "schema_version": site.get("schema_version", 1),
        "site": site.get("site", {}),
        "collections": collections,
        "pages": pages,
    }
    normalize_content_bundle(bundle)
    validate_content_bundle(bundle)
    return bundle


def validate_content_bundle(bundle: dict[str, Any]) -> None:
    if bundle.get("schema_version") != 1:
        raise ContentValidationError("Unsupported content schema version.")
    site = bundle.get("site")
    pages = bundle.get("pages")
    collections = bundle.get("collections")
    if not isinstance(site, dict) or not isinstance(pages, list) or not isinstance(collections, dict):
        raise ContentValidationError("Content bundle must include site, pages and collections.")

    page_ids: set[str] = set()
    routes: set[str] = set()
    for page in pages:
        if not isinstance(page, dict):
            raise ContentValidationError("Every page must be an object.")
        page_id = str(page.get("id", "")).strip()
        if not IDENTIFIER_PATTERN.fullmatch(page_id) or page_id in page_ids:
            raise ContentValidationError(f"Missing or duplicated page id: {page_id or '(empty)'}")
        page_ids.add(page_id)
        route = normalize_route(str(page.get("route", "")))
        if route in routes:
            raise ContentValidationError(f"Duplicated page route: {route or '/'}")
        routes.add(route)
        sections = page.get("sections", [])
        if not isinstance(sections, list):
            raise ContentValidationError(f"Page '{page_id}' sections must be a list.")
        section_ids: set[str] = set()
        for section in sections:
            if not isinstance(section, dict):
                raise ContentValidationError(f"Page '{page_id}' has an invalid section.")
            section_id = str(section.get("id", "")).strip()
            section_type = str(section.get("type", "")).strip()
            if not IDENTIFIER_PATTERN.fullmatch(section_id) or section_id in section_ids:
                raise ContentValidationError(
                    f"Page '{page_id}' has a missing or duplicated section id."
                )
            if not section_type:
                raise ContentValidationError(f"Section '{section_id}' has no type.")
            if not isinstance(section.get("data"), dict):
                raise ContentValidationError(f"Section '{section_id}' data must be an object.")
            if "visible" in section and not isinstance(section["visible"], bool):
                raise ContentValidationError(f"Section '{section_id}' visibility must be true or false.")
            section_ids.add(section_id)

    if "" not in routes:
        raise ContentValidationError("One page must use the root route.")

    for name, items in collections.items():
        if not re.fullmatch(r"[a-z0-9_]+", name) or not isinstance(items, list):
            raise ContentValidationError(f"Invalid collection: {name}")

    navigation = site.get("navigation", {})
    groups = navigation.get("groups", []) if isinstance(navigation, dict) else []
    if not isinstance(groups, list):
        raise ContentValidationError("Navigation groups must be a list.")
    navigation_ids: set[str] = set()
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("items"), list):
            raise ContentValidationError("Every navigation group must contain an item list.")
        for item in group["items"]:
            if not isinstance(item, dict) or item.get("page_id") not in page_ids:
                raise ContentValidationError("Navigation contains an unknown page reference.")
            page_id = str(item["page_id"])
            if page_id in navigation_ids:
                raise ContentValidationError(f"Page '{page_id}' appears more than once in navigation.")
            navigation_ids.add(page_id)
    subnav = navigation.get("conference_subnav", []) if isinstance(navigation, dict) else []
    if not isinstance(subnav, list) or any(page_id not in page_ids for page_id in subnav):
        raise ContentValidationError("Conference navigation contains an unknown page reference.")

    links = site.get("links", {})
    if not isinstance(links, dict):
        raise ContentValidationError("Shared links must be an object.")
    for name, href in links.items():
        if not isinstance(href, str):
            raise ContentValidationError(f"Shared link '{name}' must be text.")
        _validate_href(href, f"site.links.{name}")

    _validate_references(
        {"site": site, "collections": collections, "pages": pages},
        page_ids=page_ids,
        site_links=set(links),
        location="content",
    )


def bundle_for_editor(bundle: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(bundle)


def _atomic_json_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_content_bundle(bundle: dict[str, Any], content_root: Path | None = None) -> None:
    validate_content_bundle(bundle)
    root = content_root or CONTENT_ROOT
    site_payload = {
        "schema_version": bundle["schema_version"],
        "site": bundle["site"],
    }
    _atomic_json_write(root / "site.json", site_payload)

    collection_root = root / "collections"
    collection_root.mkdir(parents=True, exist_ok=True)
    expected_collections = set()
    for name, items in bundle["collections"].items():
        if not re.fullmatch(r"[a-z0-9_]+", name):
            raise ContentValidationError(f"Invalid collection name: {name}")
        expected_collections.add(f"{name}.json")
        _atomic_json_write(collection_root / f"{name}.json", {"items": items})
    for path in collection_root.glob("*.json"):
        if path.name not in expected_collections:
            path.unlink()

    page_root = root / "pages"
    page_root.mkdir(parents=True, exist_ok=True)
    expected_pages = set()
    for page in bundle["pages"]:
        filename = f'{page["id"]}.json'
        expected_pages.add(filename)
        _atomic_json_write(page_root / filename, page)
    for path in page_root.glob("*.json"):
        if path.name not in expected_pages:
            path.unlink()
