from __future__ import annotations

import hashlib
import json
import os
import re
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SITE_URL = os.environ.get("SITE_URL", "https://ache1312.github.io/hantavirussociety").rstrip("/")
STYLESHEET = "styles.min.css"
FONTSHEET = "fonts.min.css"
SCRIPT = "script.min.js"

OG_IMAGES: dict[str, str] = {
    "home": "ui/social-preview.jpg",
    "about": "ui/social-preview.jpg",
    "former": "ui/social-preview.jpg",
    "communications": "ui/social-preview.jpg",
    "ich2026": "ich2026/ich2026-hero-emblem.jpg",
    "keynote": "ich2026/conference-volcano.jpg",
    "programme": "ich2026/ich2026-logo-landscape.png",
    "registration": "venue/puerto-varas-waterfront.jpg",
    "venue": "venue/hotel-bellavista-window.jpg",
    "sponsors": "ich2026/pto-varas2.png",
    "committees": "ich2026/ich2026-logo-landscape.png",
    "contact": "ui/social-preview.jpg",
}

HERO_IMAGES: dict[str, str] = {
    "home": "ui/home-science-hero.webp?v=virus-fill-20260521",
    "about": "ui/home-science-hero.webp?v=virus-fill-20260521",
    "former": "former-meetings/2023-seoul-2.jpg",
    "communications": "ich2026/hantavirus-em.jpg",
    "ich2026": "ich2026/ich2026-hero-emblem.jpg",
    "keynote": "ich2026/conference-volcano.jpg",
    "programme": "ich2026/ich2026-logo-landscape.png",
    "registration": "venue/puerto-varas-waterfront.jpg",
    "venue": "venue/hotel-bellavista-window.jpg",
    "sponsors": "ich2026/pto-varas2.png",
    "committees": "ich2026/ich2026-logo-landscape.png",
}

HOME_HERO_VARIANTS = [
    (
        "current",
        "Current",
        "ui/home-science-hero.webp?v=virus-fill-20260521",
        "Large International Society for Hantaviruses logo emblem on a clean scientific background",
    ),
    (
        "emblem",
        "Emblem",
        "ui/home-hero-emblem-science.webp?v=small-emblems-20260521",
        "Premium virology background with several small logo-inspired viral forms",
    ),
    (
        "global",
        "Global",
        "ui/home-hero-global-medallion.webp?v=small-emblems-20260521",
        "Institutional research background with hundreds of small logo-inspired viral forms",
    ),
    (
        "microscopy",
        "Microscopy",
        "ui/home-hero-microscopy-aesthetic.webp?v=small-emblems-20260521",
        "Editorial microscopy background with small logo-inspired viral particles in depth",
    ),
    (
        "logo",
        "Logo base",
        "ui/home-hero-logo-background.webp",
        "Premium scientific background derived from the society logo identity",
    ),
]

VISIBLE_HOME_HERO_VARIANTS = HOME_HERO_VARIANTS[:4]

CONFERENCE_JSON_LD_TEMPLATE = """{
    "@context": "https://schema.org",
    "@type": "Event",
    "name": "International Conference on Hantaviruses 2026",
    "alternateName": "ICH2026",
    "startDate": "2026-11-02",
    "endDate": "2026-11-05",
    "eventStatus": "https://schema.org/EventScheduled",
    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
    "location": {
      "@type": "Place",
      "name": "Hotel Bellavista",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Puerto Varas",
        "addressRegion": "Los Lagos",
        "addressCountry": "CL"
      }
    },
    "organizer": {
      "@type": "Organization",
      "name": "International Society for Hantaviruses",
      "url": "__SITE_URL__"
    },
    "url": "__SITE_URL__/ich2026",
    "image": "__SITE_URL__/assets/images/ich2026/ich2026-hero-emblem.jpg",
    "description": "International Conference on Hantaviruses 2026 in Puerto Varas, Chile. Covering viral epidemiology, ecology, virus-host interactions, pathogenesis, vaccines and therapeutics."
  }"""


THEME_BOOTSTRAP = """    <script>
      (() => {
        const root = document.documentElement;
        let storedTheme = null;
        try {
          storedTheme = localStorage.getItem("ish-theme");
        } catch {}
        const theme = storedTheme === "dark" || storedTheme === "light" ? storedTheme : "light";
        root.dataset.theme = theme;
        root.style.colorScheme = theme;
      })();
    </script>"""


NAV = [
    ("about", "About ISH", "about-ish/"),
    ("former", "Former Meetings", "former-meetings/"),
    ("communications", "Communications", "communications/"),
    ("ich2026", "ICH2026", "ich2026/"),
    ("keynote", "Keynotes", "ich2026/keynote-speakers/"),
    ("programme", "Programme", "ich2026/programme/"),
    ("registration", "Registration", "ich2026/abstracts-registration/"),
    ("venue", "Venue", "ich2026/venue/"),
    ("sponsors", "Partners & Sponsors", "ich2026/partners-sponsors/"),
]

NAV_GROUPS = [
    (
        "Society",
        [
            ("about", "About ISH", "about-ish/"),
            ("former", "Former Meetings", "former-meetings/"),
            ("communications", "Communications", "communications/"),
        ],
    ),
    (
        "Conference",
        [
            ("ich2026", "ICH2026", "ich2026/"),
            ("keynote", "Keynotes", "ich2026/keynote-speakers/"),
            ("programme", "Programme", "ich2026/programme/"),
            ("registration", "Registration", "ich2026/abstracts-registration/"),
            ("venue", "Venue", "ich2026/venue/"),
            ("sponsors", "Partners & Sponsors", "ich2026/partners-sponsors/"),
        ],
    ),
]

ICH_NAV_KEYS = {"ich2026", "keynote", "programme", "registration", "venue", "sponsors"}

MEMBERSHIP_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSc0IHUnT80-qDJn2wU4pLXKQ1F_VEdcziqVL-47iGGAwsLBEA/viewform?pli=1"
CONFERENCE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfMc-cPx3hL8-Q67gN3uFLpQiZlgOD5lr03vvze29w4axGWtQ/viewform"

BOARD = [
    ("Nicole Tischler", "President ISH | Chile", "board/nicole-tischler.jpg", "https://orcid.org/0000-0002-4578-4780"),
    ("Piet Maes", "President Elect | Belgium", "board/piet-maes.jpg?v=piet-unified-css-frame-20260603", "https://orcid.org/0000-0002-4571-5232"),
    ("Colleen B. Jonsson", "Secretary ISH | USA", "board/colleen-jonsson.jpg", "https://orcid.org/0000-0002-2640-7672"),
    ("Jin Won Song", "Past-President | Korea", "board/jin-won-song.jpg", "https://orcid.org/0000-0003-0796-8332"),
    ("Satoru Arai", "Japan", "board/satoru-arai.jpg", "https://orcid.org/0000-0001-5865-0717"),
    ("Tatjana Avsic-Zupanc", "Slovenia", "board/tatjana-avsic-zupanc.jpg", "https://orcid.org/0000-0001-6243-0688"),
    ("Roger Hewson", "United Kingdom", "board/roger-hewson.jpg", "https://orcid.org/0000-0003-2273-3152"),
    ("Boris Klempa", "Slovakia", "board/boris-klempa.jpg", "https://orcid.org/0000-0002-6931-1224"),
    ("Jonas Klingstrom", "Sweden", "board/jonas-klingstrom.jpg", "https://orcid.org/0000-0001-9076-1441"),
    ("Dexin Li", "China", "board/dexin-li.jpg", ""),
    ("Mifang Liang", "China", "board/mifang-liang.jpg", ""),
    ("Alemka Markotic", "Croatia", "board/almeka-markotic.jpg", "https://orcid.org/0000-0003-4104-7940"),
    ("Valeria Martinez", "Argentina", "board/valeria-martinez.jpg", "https://orcid.org/0000-0002-4356-8136"),
    ("Gustavo Palacios", "USA", "board/gustavo-palacios.jpg", "https://orcid.org/0000-0001-5062-1938"),
    ("Anna Papa", "Greece", "board/anna-papa.jpg", "https://orcid.org/0000-0002-6643-3322"),
    ("Liudmila Yashina", "Russia", "board/liudmila-yashina.jpg", "https://orcid.org/0000-0003-2844-7835"),
    ("Connie Schmaljohn", "Honorary Member | USA", "board/connie-schmaljohn.jpg", "https://orcid.org/0000-0001-8852-5482"),
]

SCIENTIFIC_COMMITTEE = [
    ("Nicole Tischler", "President ISH", "Fundacion Ciencia & Vida / Universidad San Sebastian", "Chile", "ich2026/scientific-nicole-tischler.jpg", "https://orcid.org/0000-0002-4578-4780"),
    ("Piet Maes", "President Elect ISH", "Universite libre de Bruxelles", "Belgium", "board/piet-maes.jpg?v=piet-unified-css-frame-20260603", "https://orcid.org/0000-0002-4571-5232"),
    ("Colleen B. Jonsson", "Secretary ISH", "University of Tennessee Health Science Center", "USA", "ich2026/scientific-colleen-jonsson.jpg", "https://orcid.org/0000-0002-2640-7672"),
    ("Jin Won Song", "Past-President ISH", "Korea University College of Medicine", "Korea", "ich2026/scientific-jin-won-song.jpg", "https://orcid.org/0000-0003-0796-8332"),
    ("Satoru Arai", "Scientific Committee", "National Institute of Infectious Diseases / Japan Institute for Health Security", "Japan", "ich2026/scientific-satoru-arai.jpg", "https://orcid.org/0000-0001-5865-0717"),
    ("Steven Bradfute", "Scientific Committee", "Center for Global Health, University of New Mexico", "USA", "ich2026/scientific-steven-bradfute.jpg", "https://orcid.org/0000-0002-1985-751X"),
    ("Roger Hewson", "Scientific Committee", "UK Health Security Agency / London School of Hygiene & Tropical Medicine", "UK", "ich2026/scientific-roger-hewson.jpg", "https://orcid.org/0000-0003-2273-3152"),
    ("Boris Klempa", "Scientific Committee", "Biomedical Research Center, Slovak Academy of Sciences", "Slovakia", "ich2026/scientific-boris-klempa.jpg", "https://orcid.org/0000-0002-6931-1224"),
    ("Jonas Klingstrom", "Scientific Committee", "Linkoping University", "Sweden", "ich2026/scientific-jonas-klingstrom.jpg", "https://orcid.org/0000-0001-9076-1441"),
    ("Valeria Martinez", "Scientific Committee", "INEI / ANLIS Dr. C. G. Malbran", "Argentina", "ich2026/scientific-valeria-martinez.jpg", "https://orcid.org/0000-0002-4356-8136"),
    ("Gustavo Palacios", "Scientific Committee", "Icahn School of Medicine at Mount Sinai", "USA", "ich2026/scientific-gustavo-palacios.jpg", "https://orcid.org/0000-0001-5062-1938"),
]

LOCAL_COMMITTEE = [
    ("Jenniffer Angulo", "Local Organizing Committee", "Pontificia Universidad Catolica de Chile", "", "ich2026/local-jenniffer-angulo.jpg", "https://orcid.org/0000-0002-0471-4751"),
    ("Maria Ines Barria", "Local Organizing Committee", "Universidad San Sebastian", "Puerto Montt", "ich2026/local-maria-ines-barria.jpg", "https://orcid.org/0000-0001-6225-5971"),
    ("Mario Calvo", "Local Organizing Committee", "Universidad Austral de Chile", "Valdivia", "ich2026/local-mario-calvo.jpg", "https://orcid.org/0000-0002-1796-2236"),
    ("Marcela Ferres", "Local Organizing Committee", "Pontificia Universidad Catolica de Chile", "", "ich2026/local-marcela-ferres.jpg", "https://orcid.org/0000-0001-9415-4657"),
    ("Juan Hormazabal", "Local Organizing Committee", "Universidad del Desarrollo", "", "ich2026/local-juan-hormazabal.jpg", "https://orcid.org/0000-0003-0726-2778"),
    ("Nicole Le Corre", "Local Organizing Committee", "Pontificia Universidad Catolica de Chile", "", "ich2026/local-nicole-le-corre.jpg", "https://orcid.org/0000-0002-9361-4049"),
    ("Constanza Martinez-Valdevenito", "Local Organizing Committee", "Pontificia Universidad Catolica de Chile", "", "ich2026/local-constanza-martinez-valdevenito.jpg", "https://orcid.org/0000-0002-2836-9817"),
    ("Nicole Tischler", "Local Organizing Committee", "Fundacion Ciencia & Vida / Universidad San Sebastian", "", "ich2026/scientific-nicole-tischler.jpg", "https://orcid.org/0000-0002-4578-4780"),
    ("Fernando Torres-Perez", "Local Organizing Committee", "Pontificia Universidad Catolica de Valparaiso", "", "ich2026/local-fernando-torres-perez.jpg", "https://orcid.org/0000-0001-8655-7288"),
    ("Cecilia Vial", "Local Organizing Committee", "Universidad del Desarrollo", "", "ich2026/local-cecilia-vial.jpg", "https://orcid.org/0000-0002-0399-6144"),
    ("Pablo Vial", "Local Organizing Committee", "Universidad del Desarrollo", "", "ich2026/local-pablo-vial.jpg", "https://orcid.org/0000-0002-4135-0416"),
]

SPONSORS = [
    ("Sponsors", "BD", "https://www.bd.com/en-us/", "sponsors/poster/bd.png"),
    ("Sponsors", "Thermo Fisher Scientific", "https://www.thermofisher.com/us/en/home.html", "sponsors/poster/thermofisher-scientific.png"),
    ("Sponsors", "IMERLAB", "https://www.imerlab.cl/", "sponsors/poster/imerlab.png"),
    ("Sponsors", "Anasac", "https://anasac.cl/", "sponsors/poster/anasac.png"),
    ("Scientific societies", "Sociedad Chilena de Microbiologia", "https://somich.cl/", "sponsors/poster/somich.png"),
    ("Scientific societies", "Sociedad Chilena de Infectologia", "https://sochinf.cl/", "sponsors/poster/sociedad-chilena-infectologia.png"),
    ("Scientific societies", "Sociedad de Bioquimica y Biologia Molecular de Chile", "https://www.sbbmch.cl/", "sponsors/poster/sociedad-bioquimica.png"),
    ("Scientific societies", "International Society for Hantaviruses", SITE_URL + "/", "sponsors/poster/ish.png"),
    ("Universities & research partners", "Universidad San Sebastian", "https://www.uss.cl/", "sponsors/poster/universidad-san-sebastian.png"),
    ("Universities & research partners", "Fundacion Ciencia & Vida", "https://www.cienciavida.org/", "sponsors/poster/fundacion-ciencia-vida.png"),
    ("Universities & research partners", "Pontificia Universidad Catolica de Chile", "https://www.uc.cl/", "sponsors/poster/pontificia-universidad-catolica.png"),
    ("Universities & research partners", "Universidad del Desarrollo", "https://www.udd.cl/", "sponsors/poster/universidad-del-desarrollo.png"),
    ("Universities & research partners", "Centro Ciencia & Vida", "https://www.cienciavida.org/", "sponsors/poster/centro-ciencia-vida.png"),
    ("Universities & research partners", "ANID", "https://anid.cl/", "sponsors/poster/anid.png"),
]

SPONSOR_GROUP_LABELS = [
    ("Scientific societies", "Scientific societies"),
    ("Universities & research partners", "Universities & research partners"),
    ("Sponsors", "Sponsors"),
]

FORMER_MEETINGS = [
    ("XII", "2023", "Seoul, Republic of Korea", "International Conference on Hantaviruses", "assets/documents/former-meetings/2023-seoul-abstract-book.pdf", "former-meetings/2023-seoul-1.jpg", ""),
    ("XI", "2019", "Leuven, Belgium", "International Conference on HFRS, HPS & Hantaviruses", "assets/documents/former-meetings/2019-leuven-abstract-book.pdf", "former-meetings/2019-leuven-1.jpg", "Meeting report pending"),
    ("X", "2016", "Colorado, USA", "Abstract Book", "assets/documents/former-meetings/2016-colorado-abstract-book.pdf", "former-meetings/2016-colorado-1.jpg", "Meeting report pending"),
    ("IX", "2013", "Beijing, China", "Abstract Book", "assets/documents/former-meetings/2013-beijing-abstract-book.pdf", "former-meetings/2013-china-1.jpg", "Meeting report pending"),
    ("VIII", "2010", "Athens, Greece", "", "", "", ""),
    ("VII", "2007", "Buenos Aires, Argentina", "", "", "", ""),
    ("VI", "2004", "Seoul, Republic of Korea", "", "", "", ""),
    ("V", "2001", "Annecy, France", "", "", "", "Meeting report pending"),
    ("IV", "1998", "Atlanta, USA", "International Conference on HFRS", "", "", "Summary pending"),
    ("III", "1995", "Helsinki, Finland", "", "", "", "Meeting report pending"),
    ("II", "1992", "Beijing, China", "", "", "", "Meeting report pending"),
    ("I", "1989", "Seoul, Korea", "", "", "", "Meeting report pending"),
]

FORMER_GALLERIES = [
    (
        "XII",
        "2023",
        "Seoul, Republic of Korea",
        [
            "former-meetings/2023-seoul-1.jpg",
            "former-meetings/2023-seoul-2.jpg",
            "former-meetings/2023-seoul-3.jpg",
        ],
    ),
    (
        "XI",
        "2019",
        "Leuven, Belgium",
        [
            "former-meetings/2019-leuven-1.jpg",
            "former-meetings/2019-leuven-2.jpg",
        ],
    ),
    (
        "X",
        "2016",
        "Colorado, USA",
        [
            "former-meetings/2016-colorado-1.jpg",
            "former-meetings/2016-colorado-2.jpg",
            "former-meetings/2016-colorado-3.jpg",
        ],
    ),
    (
        "IX",
        "2013",
        "Beijing, China",
        [
            "former-meetings/2013-china-1.jpg",
            "former-meetings/2013-china-2.jpg",
            "former-meetings/2013-china-3.jpg",
        ],
    ),
]

TRAVEL_LINKS = [
    ("hotel", "Hotel Bellavista", "Conference venue and event facilities.", "https://hotelbellavista.cl/reuniones-y-eventos-corporativos-2/"),
    ("map-pin", "Venue map", "Av. Vicente Perez Rosales #060, Puerto Varas.", "https://goo.gl/maps/dv2jUC4hSGLvr2Ld9"),
    ("plane", "Santiago airport", "International arrival at Arturo Merino Benítez Airport.", "https://thesantiagoairport.com/"),
    ("route", "Santiago day trips", "Optional stop-over ideas near Santiago.", "https://www.tripadvisor.com/Attractions-g294305-Activities-c42-t205-Santiago_Santiago_Metropolitan_Region.html"),
    ("route", "Santiago tours", "Additional tours and day activities in Santiago.", "https://www.viator.com/Santiago/d713?pid=P00095352&mcid=42383&medium=link&campaign=scltours"),
    ("car", "Santiago airport transfer", "SCL transfer service for travelers staying overnight in Santiago.", "https://ww2.trasladoaeropuerto.cl/"),
    ("message", "Santiago transfer WhatsApp", "Direct WhatsApp contact for SCL transfer reservations.", "https://api.whatsapp.com/send?phone=56976053701&text=hola,%20lo%20contacto%20desde%20la%20p%C3%A1gina%20web"),
    ("mail", "Santiago transfer email", "SCL transfer contact: reservas@trasladoaeropuerto.cl", "mailto:reservas@trasladoaeropuerto.cl"),
    ("car", "Survip transfer", "Transfer service from Puerto Montt airport to Puerto Varas.", "https://www.survip.cl/transfer-aeropuerto-puerto-montt-a-puerto-varas.php"),
]

TRAVEL_ICONS = {
    "car": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 17h14l-1.6-5.2A3 3 0 0 0 14.5 10h-5a3 3 0 0 0-2.9 1.8L5 17Z"/><path d="M7 17v2"/><path d="M17 17v2"/><path d="M6.5 14h11"/><circle cx="8" cy="17" r="1"/><circle cx="16" cy="17" r="1"/></svg>',
    "hotel": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v15"/><path d="M16 10h2a2 2 0 0 1 2 2v9"/><path d="M8 8h.01"/><path d="M12 8h.01"/><path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M9 21v-4h3v4"/><path d="M3 21h18"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="6" width="16" height="12" rx="2"/><path d="m4 8 8 6 8-6"/></svg>',
    "map-pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "message": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 18.5 6.2 15A7 7 0 1 1 9 17.4L5 18.5Z"/><path d="M9 10h6"/><path d="M9 13h4"/></svg>',
    "plane": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10.5 20 13 13l7-2.5a1.3 1.3 0 0 0 0-2.5L4 3l3.8 7L4 17l6.5-2.4V20Z"/></svg>',
    "route": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 6H14a3 3 0 0 1 0 6h-4a3 3 0 0 0 0 6h5.5"/></svg>',
}

LOCATION_CAROUSEL_IMAGES = [
    ("01", "Puerto Varas and Osorno Volcano", "Osorno Volcano and Puerto Varas church by Lake Llanquihue", "ich2026/from-zip/pvaras.webp"),
    ("02", "Lake District setting", "Panoramic Puerto Varas view with Lake Llanquihue and Osorno Volcano", "ich2026/from-zip/pvaras2.jpg"),
    ("03", "Lake Llanquihue activities", "Kayaks on Lake Llanquihue near Puerto Varas", "ich2026/from-zip/sea-kayak-puerto-varas.jpg"),
]


def prefix_for(out_path: str) -> str:
    parent = Path(out_path).parent
    return "" if str(parent) == "." else "../" * len(parent.parts)


def img(prefix: str, asset_path: str) -> str:
    return f"{prefix}assets/images/{asset_path}"


def load_image_manifest() -> dict[str, dict[str, object]]:
    manifest_path = ROOT / "assets" / "images" / "optimized" / "manifest.json"
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


IMAGE_MANIFEST = load_image_manifest()
IMAGE_DIMENSION_FALLBACKS = {
    "ui/home-hero-emblem-science.webp": (1855, 848),
    "ui/home-hero-global-medallion.webp": (1855, 848),
    "ui/home-hero-microscopy-aesthetic.webp": (1855, 848),
    "ui/home-hero-logo-background.webp": (1855, 848),
}
FILE_VERSION_CACHE: dict[str, str] = {}


def strip_css_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def minify_css(css: str) -> str:
    css = strip_css_comments(css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>~])\s*", r"\1", css)
    css = re.sub(r";}", "}", css)
    return css.strip() + "\n"


def strip_js_comments(source: str) -> str:
    result: list[str] = []
    i = 0
    quote = ""
    escaped = False
    while i < len(source):
        char = source[i]
        next_char = source[i + 1] if i + 1 < len(source) else ""

        if quote:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            i += 1
            continue

        if char in {"'", '"', "`"}:
            quote = char
            result.append(char)
            i += 1
            continue

        if char == "/" and next_char == "/":
            i += 2
            while i < len(source) and source[i] not in "\r\n":
                i += 1
            continue

        if char == "/" and next_char == "*":
            i += 2
            while i + 1 < len(source) and not (source[i] == "*" and source[i + 1] == "/"):
                i += 1
            i += 2
            continue

        result.append(char)
        i += 1
    return "".join(result)


def minify_js(source: str) -> str:
    js = strip_js_comments(source)
    result: list[str] = []
    i = 0
    quote = ""
    escaped = False
    punct = set("{}()[].;,:?=<>+-*/%&|!")

    while i < len(js):
        char = js[i]

        if quote:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            i += 1
            continue

        if char in {"'", '"', "`"}:
            quote = char
            result.append(char)
            i += 1
            continue

        if char.isspace():
            next_index = i + 1
            while next_index < len(js) and js[next_index].isspace():
                next_index += 1
            previous = result[-1] if result else ""
            next_char = js[next_index] if next_index < len(js) else ""
            if previous and next_char and previous not in punct and next_char not in punct:
                result.append(" ")
            i = next_index
            continue

        if char in punct and result and result[-1] == " ":
            result.pop()
        result.append(char)
        i += 1

    return "".join(result).strip() + "\n"


def minify_static_assets() -> None:
    (ROOT / STYLESHEET).write_text(minify_css((ROOT / "styles.css").read_text(encoding="utf-8")), encoding="utf-8")
    (ROOT / FONTSHEET).write_text(minify_css((ROOT / "fonts.css").read_text(encoding="utf-8")), encoding="utf-8")
    (ROOT / SCRIPT).write_text(minify_js((ROOT / "script.js").read_text(encoding="utf-8")), encoding="utf-8")


def file_version(path: str) -> str:
    if path not in FILE_VERSION_CACHE:
        digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        FILE_VERSION_CACHE[path] = digest[:12]
    return FILE_VERSION_CACHE[path]


def asset_key(asset_path: str) -> str:
    return asset_path.split("?", 1)[0]


def asset_query_suffix(asset_path: str) -> str:
    parts = asset_path.split("?", 1)
    return f"?{parts[1]}" if len(parts) == 2 else ""


def format_attrs(values: dict[str, object]) -> str:
    parts = []
    for key, value in values.items():
        if value is None or (value == "" and key != "alt"):
            continue
        name = key[:-1] if key.endswith("_") else key
        parts.append(f'{name.replace("_", "-")}="{escape(str(value), quote=True)}"')
    return " ".join(parts)


def optimized_source(prefix: str, asset_path: str, sizes: str, format_name: str) -> str:
    manifest = IMAGE_MANIFEST.get(asset_key(asset_path))
    if not manifest:
        return ""
    formats = manifest.get("formats", {})  # type: ignore[assignment]
    variants = formats.get(format_name, []) if isinstance(formats, dict) else []
    if not variants and format_name == "webp":
        variants = manifest.get("variants", [])  # type: ignore[assignment]
    if not variants:
        return ""
    query_suffix = asset_query_suffix(asset_path)
    srcset = ", ".join(
        f'{prefix}assets/images/{variant["path"]}{query_suffix} {variant["width"]}w' for variant in variants
    )
    return f'<source {format_attrs({"type": f"image/{format_name}", "srcset": srcset, "sizes": sizes})}>'


def optimized_image_url(prefix: str, asset_path: str, *, format_name: str = "webp", max_width: int = 1280) -> str:
    manifest = IMAGE_MANIFEST.get(asset_key(asset_path))
    if not manifest:
        return img(prefix, asset_path)
    formats = manifest.get("formats", {})  # type: ignore[assignment]
    variants = formats.get(format_name, []) if isinstance(formats, dict) else []
    if not variants:
        variants = manifest.get("variants", [])  # type: ignore[assignment]
    if not variants:
        return img(prefix, asset_path)
    sorted_variants = sorted(variants, key=lambda item: item["width"])
    selected = next((variant for variant in sorted_variants if variant["width"] >= max_width), sorted_variants[-1])
    return f'{prefix}assets/images/{selected["path"]}{asset_query_suffix(asset_path)}'


def responsive_image(
    prefix: str,
    asset_path: str,
    alt: str,
    *,
    class_name: str = "",
    picture_class: str = "responsive-image",
    loading: str = "",
    decoding: str = "",
    fetchpriority: str = "",
    sizes: str = "100vw",
    aria_hidden: str = "",
    picture_attrs_extra: dict[str, object] | None = None,
) -> str:
    manifest = IMAGE_MANIFEST.get(asset_key(asset_path))
    image_attrs: dict[str, object] = {
        "class": class_name,
        "src": img(prefix, asset_path),
        "alt": alt,
        "loading": loading,
        "decoding": decoding,
        "fetchpriority": fetchpriority,
        "aria_hidden": aria_hidden,
    }
    if manifest:
        image_attrs["width"] = manifest["width"]
        image_attrs["height"] = manifest["height"]
    elif asset_key(asset_path) in IMAGE_DIMENSION_FALLBACKS:
        width, height = IMAGE_DIMENSION_FALLBACKS[asset_key(asset_path)]
        image_attrs["width"] = width
        image_attrs["height"] = height
    picture_values: dict[str, object] = {"class": picture_class}
    if picture_attrs_extra:
        picture_values.update(picture_attrs_extra)
    picture_attrs = format_attrs(picture_values)
    picture_attrs = f" {picture_attrs}" if picture_attrs else ""
    sources = optimized_source(prefix, asset_path, sizes, "avif") + optimized_source(prefix, asset_path, sizes, "webp")
    return f'<picture{picture_attrs}>{sources}<img {format_attrs(image_attrs)}></picture>'


def preload_image(prefix: str, asset_path: str, sizes: str = "100vw") -> str:
    manifest = IMAGE_MANIFEST.get(asset_key(asset_path))
    if not manifest:
        return f'    <link rel="preload" as="image" href="{img(prefix, asset_path)}" fetchpriority="high">'
    formats = manifest.get("formats", {})  # type: ignore[assignment]
    format_name = "avif" if isinstance(formats, dict) and formats.get("avif") else "webp"
    variants = formats.get(format_name, []) if isinstance(formats, dict) else manifest.get("variants", [])  # type: ignore[assignment]
    if not variants:
        return f'    <link rel="preload" as="image" href="{img(prefix, asset_path)}" fetchpriority="high">'
    variants = sorted(variants, key=lambda item: item["width"])
    query_suffix = asset_query_suffix(asset_path)
    srcset = ", ".join(
        f'{prefix}assets/images/{variant["path"]}{query_suffix} {variant["width"]}w' for variant in variants
    )
    href = f'{prefix}assets/images/{variants[-1]["path"]}{query_suffix}'
    return f'<link {format_attrs({"rel": "preload", "as": "image", "href": href, "type": f"image/{format_name}", "imagesrcset": srcset, "imagesizes": sizes, "fetchpriority": "high"})}>'


def local(prefix: str, path: str = "") -> str:
    return f"{prefix}{path}"


def external_attrs(href: str) -> str:
    if href.startswith(("http://", "https://")) and not href.startswith(SITE_URL):
        return ' target="_blank" rel="noreferrer"'
    return ""


def contact_href(prefix: str) -> str:
    return local(prefix, "about-ish/#contact")


def attrs(**values: str) -> str:
    return format_attrs(values)


def conference_json_ld() -> str:
    return CONFERENCE_JSON_LD_TEMPLATE.replace("__SITE_URL__", SITE_URL)


def travel_icon(name: str) -> str:
    return f'<span class="travel-link-icon" aria-hidden="true">{TRAVEL_ICONS[name]}</span>'


def travel_link_card(icon: str, label: str, description: str, href: str) -> str:
    target = "" if href.startswith("mailto:") else ' target="_blank" rel="noreferrer"'
    return (
        f'<a class="travel-link" href="{escape(href, quote=True)}"{target}>'
        f'{travel_icon(icon)}'
        f'<span class="travel-link-copy"><strong>{escape(label)}</strong><small>{escape(description)}</small></span>'
        "</a>"
    )


def clean_output(content: str) -> str:
    return "\n".join(line.rstrip() for line in content.splitlines()) + "\n"


def minify_html(content: str) -> str:
    content = re.sub(r"<!--.*?-->", "", content, flags=re.S)
    content = re.sub(r">\s+<", "><", content)
    content = re.sub(r"\s{2,}", " ", content)
    return content.strip() + "\n"


def header(prefix: str, active: str) -> str:
    nav_groups = []
    for group_label, links in NAV_GROUPS:
        items = []
        for key, label, href in links:
            current = ' aria-current="page"' if key == active else ""
            items.append(f'<a href="{local(prefix, href)}" data-nav="{key}"{current}>{escape(label)}</a>')
        nav_groups.append(
            f'<div class="nav-group" data-nav-group="{escape(group_label.lower())}"><span>{escape(group_label)}</span><div>{"".join(items)}</div></div>'
        )
    return f"""
    <header class="site-header" data-header>
      <a class="brand" href="{local(prefix)}" aria-label="International Society for Hantaviruses">
        {responsive_image(prefix, "ui/logo.png", "International Society for Hantaviruses logo", class_name="brand-logo", loading="eager", decoding="async", sizes="140px")}
        <span class="brand-copy">
          <strong>International Society</strong>
          <span>for Hantaviruses</span>
        </span>
      </a>
      <button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="site-menu" data-menu-toggle>
        <span></span>
        <span></span>
        <span></span>
        <span class="sr-only">Menu</span>
      </button>
      <nav class="site-nav" id="site-menu" aria-label="Primary navigation" data-menu>
        {"".join(nav_groups)}
      </nav>
      <button class="theme-toggle" type="button" aria-label="Light mode active. Switch to dark mode." aria-pressed="false" title="Light mode active. Switch to dark mode." data-theme-tooltip="Light mode active. Switch to dark mode." data-theme-toggle>
        <span class="theme-icon theme-icon-sun" aria-hidden="true"></span>
        <span class="theme-icon theme-icon-moon" aria-hidden="true"></span>
        <span class="sr-only" data-theme-label>Light mode active. Switch to dark mode.</span>
      </button>
    </header>"""


def ich_subnav(prefix: str, active: str) -> str:
    links = []
    for key, label, href in NAV:
        if key not in ICH_NAV_KEYS:
            continue
        current = ' aria-current="page"' if key == active else ""
        links.append(f'<a href="{local(prefix, href)}" data-nav="{key}"{current}>{escape(label)}</a>')
    return f"""
      <nav class="subnav-strip" aria-label="ICH2026 section navigation">
        <span>ICH2026</span>
        <div>{"".join(links)}</div>
      </nav>"""


def footer(prefix: str) -> str:
    return f"""
    <footer class="site-footer-rich">
      <div>
        {responsive_image(prefix, "ui/logo.png", "International Society for Hantaviruses logo", loading="lazy", decoding="async", sizes="190px")}
        <p>Website of the International Society for Hantaviruses.</p>
      </div>
      <nav aria-label="Site pages">
        <strong>Site</strong>
        <a href="{local(prefix, "about-ish/")}">About ISH</a>
        <a href="{local(prefix, "former-meetings/")}">Former Meetings</a>
        <a href="{local(prefix, "communications/")}">Communications</a>
        <a href="{local(prefix, "ich2026/")}">ICH2026</a>
        <a href="{local(prefix, "ich2026/abstracts-registration/")}">Registration</a>
        <a href="{local(prefix, "ich2026/#committees")}">Committees</a>
      </nav>
      <nav aria-label="Contact and actions">
        <strong>Contact</strong>
        <a href="mailto:ish@hantavirussociety.org">Contact ISH: ish@hantavirussociety.org</a>
        <a href="mailto:ICH2026@hantavirussociety.org">Contact ICH2026: ICH2026@hantavirussociety.org</a>
        <a href="{MEMBERSHIP_FORM}" target="_blank" rel="noreferrer">Apply for ISH membership</a>
        <a href="{CONFERENCE_FORM}" target="_blank" rel="noreferrer">ICH2026 registration form</a>
      </nav>
    </footer>"""


def doc(out_path: str, active: str, title: str, description: str, body: str) -> str:
    prefix = prefix_for(out_path)
    subnav = ich_subnav(prefix, active) if active in ICH_NAV_KEYS else ""
    hero_preload = preload_image(prefix, HERO_IMAGES[active]) if active in HERO_IMAGES else ""

    page_dir = str(Path(out_path).parent)
    canonical = SITE_URL + "/" if page_dir == "." else f"{SITE_URL}/{page_dir}/"
    og_image = SITE_URL + "/assets/images/" + OG_IMAGES.get(active, "ui/home-science-hero.webp")

    json_ld = ""
    if active in ICH_NAV_KEYS:
        json_ld = f'\n    <script type="application/ld+json">{conference_json_ld()}</script>'

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{escape(description)}">
    <title>{escape(title)}</title>
    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{escape(title)}">
    <meta property="og:description" content="{escape(description)}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:site_name" content="International Society for Hantaviruses">
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{escape(title)}">
    <meta name="twitter:description" content="{escape(description)}">
    <meta name="twitter:image" content="{og_image}">
    <!-- Canonical -->
    <link rel="canonical" href="{canonical}">
    <link rel="icon" type="image/svg+xml" href="{prefix}assets/icons/ish-favicon.svg?v={file_version("assets/icons/ish-favicon.svg")}">
    <link rel="icon" href="{prefix}favicon.ico?v={file_version("favicon.ico")}" sizes="any">
    <link rel="icon" type="image/png" sizes="256x256" href="{prefix}assets/icons/ish-icon-256.png?v={file_version("assets/icons/ish-icon-256.png")}">
    <link rel="icon" type="image/png" sizes="512x512" href="{prefix}assets/icons/ish-icon-512.png?v={file_version("assets/icons/ish-icon-512.png")}">
    <link rel="apple-touch-icon" sizes="180x180" href="{prefix}assets/icons/apple-touch-icon.png?v={file_version("assets/icons/apple-touch-icon.png")}">
    <link rel="manifest" href="{prefix}site.webmanifest?v={file_version("site.webmanifest")}">
{hero_preload}
    <link rel="preload" href="{prefix}assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="{prefix}assets/fonts/source-serif-4-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="{prefix}assets/fonts/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="{prefix}{FONTSHEET}?v={file_version(FONTSHEET)}">
{THEME_BOOTSTRAP}
    <link rel="stylesheet" href="{prefix}{STYLESHEET}?v={file_version(STYLESHEET)}">{json_ld}
  </head>
  <body data-page="{active}">
    <div class="scroll-progress" aria-hidden="true"></div>
    <a class="skip-link" href="#main-content">Skip to main content</a>
{header(prefix, active)}
    <div class="menu-backdrop" data-menu-backdrop hidden></div>
{subnav}
    <main id="main-content" tabindex="-1">
{body}
    </main>
{footer(prefix)}
    <button class="back-to-top" aria-label="Back to top" title="Back to top">↑</button>
    <script src="{prefix}{SCRIPT}?v={file_version(SCRIPT)}" defer></script>
  </body>
</html>
"""


def home_page(
    prefix: str,
    hero_image: str = "ui/home-science-hero.webp?v=virus-fill-20260521",
    hero_alt: str = "Large International Society for Hantaviruses logo emblem on a clean scientific background",
) -> str:
    hero_media = responsive_image(
        prefix,
        hero_image,
        hero_alt,
        picture_class="hero-media is-active",
        loading="eager",
        decoding="async",
        fetchpriority="high",
        sizes="100vw",
        picture_attrs_extra={
            "aria_hidden": "false",
        },
    )

    return f"""
      <section class="hero" aria-labelledby="hero-title" data-active-hero="0">
        <div class="hero-slides">
          {hero_media}
        </div>
        <div class="hero-overlay"></div>
        <div class="hero-content reveal is-visible">
          <p class="eyebrow">Research collaboration since 1989</p>
          <h1 id="hero-title">International Society for Hantaviruses</h1>
          <p class="hero-lede">A global scientific network advancing hantavirus research, clinical knowledge and international collaboration.</p>
          <div class="hero-actions" aria-label="Primary actions">
            <a class="button button-primary" href="{local(prefix, "ich2026/")}">ICH2026 in Chile</a>
            <a class="button button-secondary" href="{MEMBERSHIP_FORM}" target="_blank" rel="noreferrer">Apply for membership</a>
            <a class="button button-ghost" href="{local(prefix, "ich2026/abstracts-registration/")}">Abstracts & registration</a>
          </div>
        </div>
        <aside class="hero-panel" aria-label="ICH2026 conference brief">
          <div class="hero-panel-kicker">ICH2026</div>
          <span class="hero-panel-title">International Conference on Hantaviruses</span>
          <strong class="hero-panel-date">Nov 2-5, 2026</strong>
          <div class="hero-panel-meta" aria-label="Conference location and venue">
            <span>Puerto Varas, Chile</span>
            <span>Hotel Bellavista</span>
          </div>
          <div class="countdown" data-countdown="2026-11-02" aria-label="Time until ICH2026">
            <div class="countdown-unit"><span class="countdown-val" data-unit="days">--</span><span class="countdown-label">Days</span></div>
            <div class="countdown-unit"><span class="countdown-val" data-unit="hours">--</span><span class="countdown-label">Hours</span></div>
            <div class="countdown-unit"><span class="countdown-val" data-unit="minutes">--</span><span class="countdown-label">Minutes</span></div>
          </div>
          <a class="hero-panel-link" href="{local(prefix, "ich2026/programme/")}">Programme</a>
        </aside>
      </section>
      <section class="section intro-band">
        <div class="section-shell two-column">
          <div class="section-heading reveal">
            <p class="eyebrow">About ISH</p>
            <h2>Science-led coordination for a global zoonotic disease community.</h2>
          </div>
          <div class="prose reveal">
            <p>The International Society for Hantaviruses promotes knowledge on hantaviruses and associated diseases through research exchange, training and international scientific cooperation.</p>
            <p>The society connects experts in epidemiology, ecology, viral replication, host-pathogen interaction, pathogenesis, diagnostics, clinical management, vaccines and therapeutics.</p>
          </div>
        </div>
        <div class="section-shell society-gallery single-image" aria-label="ISH visual archive">
          <figure class="reveal">
            {responsive_image(prefix, "ui/society-archive-2.png", "ICH2023 Seoul meeting participants", loading="lazy", decoding="async", sizes="(max-width: 780px) 100vw, 1180px")}
            <figcaption>ICH2023 Seoul | Republic of Korea</figcaption>
          </figure>
        </div>
      </section>
      <section class="section data-section">
        <div class="section-shell">
          <div class="section-heading compact reveal">
            <p class="eyebrow">Research focus</p>
            <h2>A practical agenda for hantavirus science.</h2>
          </div>
          <div class="focus-grid" role="list">
            <a class="focus-item reveal" role="listitem" href="{local(prefix, "ich2026/programme/")}"><span>01</span><h3>Epidemiology & ecology</h3><p>Tracking viral diversity, reservoirs, climate influence and regional transmission dynamics.</p><strong>Programme themes</strong></a>
            <a class="focus-item reveal" role="listitem" href="{local(prefix, "ich2026/programme/")}"><span>02</span><h3>Virus-host biology</h3><p>Understanding replication, immune response, pathogenesis and host-pathogen interaction.</p><strong>Programme themes</strong></a>
            <a class="focus-item reveal" role="listitem" href="{local(prefix, "ich2026/programme/")}"><span>03</span><h3>Diagnostics & clinical management</h3><p>Improving early diagnosis, clinical management and risk assessment after exposure.</p><strong>Programme themes</strong></a>
            <a class="focus-item reveal" role="listitem" href="{local(prefix, "ich2026/programme/")}"><span>04</span><h3>Vaccines & therapeutics</h3><p>Accelerating translational work on prevention, treatment and preparedness.</p><strong>Programme themes</strong></a>
          </div>
        </div>
      </section>
      <section class="section research-domains">
        <div class="section-shell research-domain-layout">
          <div class="section-heading reveal">
            <p class="eyebrow">Scientific domains</p>
            <h2>From field ecology to clinical preparedness.</h2>
          </div>
          <div class="domain-list reveal" aria-label="Hantavirus research domains">
            <a href="{local(prefix, "ich2026/programme/")}">Reservoir ecology</a>
            <a href="{local(prefix, "ich2026/programme/")}">Viral evolution</a>
            <a href="{local(prefix, "ich2026/programme/")}">Host response</a>
            <a href="{local(prefix, "ich2026/programme/")}">Diagnostics</a>
            <a href="{local(prefix, "ich2026/programme/")}">Clinical management</a>
            <a href="{local(prefix, "ich2026/programme/")}">Vaccines</a>
            <a href="{local(prefix, "ich2026/programme/")}">Therapeutics</a>
          </div>
        </div>
      </section>
      <section class="section committees">
        <div class="section-shell">
          <div class="section-heading compact reveal">
            <p class="eyebrow">International Advisory Board</p>
            <h2>A global board connecting countries affected by hantavirus disease.</h2>
          </div>
          {advisory_grid(prefix)}
        </div>
      </section>
      <section class="section contact-band">
        <div class="section-shell contact-layout">
          <div class="section-heading reveal">
            <p class="eyebrow">Membership</p>
            <h2>Join the international hantavirus research network.</h2>
          </div>
          <div class="contact-actions reveal">
            <a class="button button-primary" href="{MEMBERSHIP_FORM}" target="_blank" rel="noreferrer">Apply for ISH membership</a>
            <a class="button button-secondary light" href="{contact_href(prefix)}">Contact ICH2026</a>
          </div>
        </div>
      </section>"""


def advisory_grid(prefix: str) -> str:
    cards = []
    for index, (name, role, image, href) in enumerate(BOARD):
        if "|" in role:
            title, country = [part.strip() for part in role.split("|", 1)]
        else:
            title, country = "International Advisory Board", role
        heading = f'<a href="{href}" target="_blank" rel="noreferrer">{escape(name)}</a>' if href else escape(name)
        officer_class = " advisor-officer" if index < 4 else ""
        honorary_class = " advisor-honorary" if name == "Connie Schmaljohn" else ""
        cards.append(
            f"""
            <article class="advisor{officer_class}{honorary_class} reveal" role="listitem">
              <div class="advisor-photo">{responsive_image(prefix, image, name, loading="lazy", decoding="async", sizes="(max-width: 520px) 128px, (max-width: 780px) 144px, (max-width: 1060px) 180px, 280px")}</div>
              <div class="advisor-copy">
                <span class="advisor-location">{escape(country)}</span>
                <h3>{heading}</h3>
                <p>{escape(title)}</p>
              </div>
            </article>"""
        )
    return f'<div class="advisory-grid" role="list">{"".join(cards)}</div>'


def page_hero(
    prefix: str,
    eyebrow: str,
    title: str,
    lede: str,
    image: str,
    ctas: list[tuple[str, str, str]] | None = None,
    breadcrumbs: list[tuple[str, str | None]] | None = None,
    image_credit: str = "",
) -> str:
    actions = ""
    if ctas:
        links = "".join(
            f'<a class="button {klass}" href="{href}"{external_attrs(href)}>{escape(label)}</a>'
            for label, href, klass in ctas
        )
        actions = f'<div class="hero-actions page-actions">{links}</div>'
    breadcrumb_html = ""
    if breadcrumbs:
        items = []
        for label, href in breadcrumbs:
            if href:
                items.append(f'<li><a href="{href}">{escape(label)}</a></li>')
            else:
                items.append(f'<li aria-current="page">{escape(label)}</li>')
        breadcrumb_html = f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'
    return f"""
      <section class="page-hero">
        {responsive_image(prefix, image, "", class_name="page-hero-bg", loading="eager", decoding="async", sizes="100vw", aria_hidden="true")}
        <div class="page-hero-overlay"></div>
        <div class="page-hero-copy reveal is-visible">
          {breadcrumb_html}
          <p class="eyebrow">{escape(eyebrow)}</p>
          <h1>{escape(title)}</h1>
          <p class="hero-lede">{escape(lede)}</p>
          {actions}
        </div>
        {f'<p class="page-hero-credit">{escape(image_credit)}</p>' if image_credit else ''}
      </section>"""


def committee_grid(
    prefix: str,
    people: list[tuple[str, str, str, str, str, str]],
    class_name: str = "committee-people-grid",
) -> str:
    cards = []
    for name, role, affiliation, location, image, href in people:
        location_html = f"<span>{escape(location)}</span>" if location else ""
        cards.append(
            f"""
            <article class="committee-person reveal" role="listitem">
              {responsive_image(prefix, image, name, loading="lazy", decoding="async", sizes="(max-width: 520px) 112px, (max-width: 780px) 128px, 180px")}
              <div>
                <h3><a href="{href}" target="_blank" rel="noreferrer">{escape(name)}</a></h3>
                <p>{escape(role)}</p>
                <span>{escape(affiliation)}</span>
                {location_html}
              </div>
            </article>"""
        )
    return f'<div class="{class_name}" role="list">{"".join(cards)}</div>'


def committee_teaser(prefix: str) -> str:
    return f"""
      <section class="section committee-teaser">
        <div class="section-shell committee-teaser-layout">
          <div class="section-heading reveal">
            <p class="eyebrow">Organizing Committees</p>
            <h2>Scientific and local teams coordinating ICH2026.</h2>
            <p>Committee details now live on a dedicated page so the conference homepage stays focused and easy to scan.</p>
            <a class="button button-primary" href="{local(prefix, "ich2026/organizing-committees/")}">View committees</a>
          </div>
        </div>
      </section>"""


def committee_directory_section(prefix: str, section_id: str | None = None) -> str:
    scientific_people = committee_grid(prefix, SCIENTIFIC_COMMITTEE, "committee-people-grid committee-directory-grid")
    local_people = committee_grid(prefix, LOCAL_COMMITTEE, "committee-people-grid committee-directory-grid")
    id_attr = f' id="{escape(section_id)}"' if section_id else ""
    return f"""
      <section class="section committees committee-directory ich-committee-inline"{id_attr}>
        <div class="section-shell">
          <div class="section-heading compact reveal">
            <p class="eyebrow">Organizing Committees</p>
            <h2>International scientific direction and Chilean local organization.</h2>
            <p>Scientific and local teams coordinating ICH2026 in Puerto Varas.</p>
          </div>
          <div class="committee-tabs reveal" role="group" aria-label="Filter committees">
            <button type="button" class="is-active" data-committee-filter="all">All</button>
            <button type="button" data-committee-filter="scientific">Scientific</button>
            <button type="button" data-committee-filter="local">Local</button>
          </div>
          <div class="committee-directory-columns" data-committee-view="all">
            <div class="committee-section" data-committee-section="scientific">
              <div class="committee-label reveal">
                <span>Scientific Committee</span>
                <p>International scientific direction for the conference programme.</p>
              </div>
              {scientific_people}
            </div>
            <div class="committee-section" data-committee-section="local">
              <div class="committee-label reveal">
                <span>Local Organizing Committee</span>
                <p>Chilean host institutions coordinating the Puerto Varas meeting.</p>
              </div>
              {local_people}
            </div>
          </div>
        </div>
      </section>"""


def location_carousel(prefix: str) -> str:
    total = len(LOCATION_CAROUSEL_IMAGES)
    slides: list[str] = []
    thumbs: list[str] = []
    dots: list[str] = []

    for index, (number, title, alt, image_path) in enumerate(LOCATION_CAROUSEL_IMAGES):
        active_class = " is-active" if index == 0 else ""
        aria_hidden = "false" if index == 0 else "true"
        aria_pressed = "true" if index == 0 else "false"
        safe_title = escape(title)
        safe_label = escape(f"Show {title}", quote=True)

        slides.append(
            f"""
            <figure class="location-slide{active_class}" data-location-slide aria-hidden="{aria_hidden}">
              {responsive_image(prefix, image_path, alt, loading="lazy", decoding="async", sizes="(max-width: 780px) 92vw, 900px")}
              <figcaption><span>{number} / {total:02d}</span><strong>{safe_title}</strong></figcaption>
            </figure>"""
        )
        thumbs.append(
            f"""
            <button class="location-thumb{active_class}" type="button" data-location-control="{index}" aria-pressed="{aria_pressed}" aria-label="{safe_label}">
              {responsive_image(prefix, image_path, alt, loading="lazy", decoding="async", picture_class="location-thumb-image", sizes="(max-width: 780px) 23vw, 160px")}
              <span><small>{number}</small>{safe_title}</span>
            </button>"""
        )
        dots.append(
            f'<button class="location-carousel-dot{active_class}" type="button" data-location-control="{index}" aria-pressed="{aria_pressed}" aria-label="{safe_label}"><span class="sr-only">{safe_label}</span></button>'
        )

    return f"""
        <div class="section-shell location-carousel reveal" data-location-carousel aria-label="Puerto Varas location carousel">
          <div class="location-carousel-frame">
            <div class="location-carousel-stage" tabindex="0">
              {"".join(slides)}
              <div class="location-carousel-actions" aria-label="Location gallery controls">
                <button class="location-carousel-arrow is-prev" type="button" data-location-prev aria-label="Previous location photograph"><span aria-hidden="true"></span><span class="sr-only">Previous location photograph</span></button>
                <div class="location-carousel-dots" role="group" aria-label="Select location photograph">
                  {"".join(dots)}
                </div>
                <button class="location-carousel-arrow is-next" type="button" data-location-next aria-label="Next location photograph"><span aria-hidden="true"></span><span class="sr-only">Next location photograph</span></button>
              </div>
            </div>
            <div class="location-carousel-thumbs" aria-label="Location photographs">
              {"".join(thumbs)}
            </div>
          </div>
        </div>"""


def ich2026_page(prefix: str) -> str:
    return f"""
      <section class="ich-hero" aria-labelledby="ich-title">
        {responsive_image(prefix, "ich2026/ich2026-hero-emblem.jpg", "ICH2026 conference visual identity emblem on a scientific blue background", class_name="ich-hero-bg", fetchpriority="high", sizes="100vw")}
        <div class="ich-hero-overlay"></div>
        <div class="ich-hero-copy reveal is-visible">
          <p class="eyebrow">International Conference on Hantaviruses</p>
          <h1 id="ich-title">Puerto Varas | Chile</h1>
          <p class="hero-lede">November 2-5 2026</p>
          <div class="ich-hero-meta" aria-label="Conference details">
            <span>Venue & Location</span>
            <strong class="ich-hero-map-line">
              <span>Hotel Bellavista, Lake District</span>
              <a class="text-link inline-map-link" href="https://goo.gl/maps/dv2jUC4hSGLvr2Ld9" target="_blank" rel="noreferrer" aria-label="Open Hotel Bellavista in Google Maps">{travel_icon("map-pin")}<span>Open map</span></a>
            </strong>
            <span>Specialized workshop</span>
            <strong>Andes Virus, November 5</strong>
          </div>
          <div class="hero-actions page-actions">
            <a class="button button-primary" href="{local(prefix, "ich2026/abstracts-registration/")}">Abstracts & registration</a>
            <a class="button button-secondary" href="{local(prefix, "ich2026/programme/")}">Scientific programme</a>
            <a class="button button-secondary" href="{local(prefix, "ich2026/venue/")}">Venue</a>
          </div>
        </div>
      </section>
      <section class="conference-summary" aria-label="ICH2026 quick facts">
        <div class="summary-item"><span>Dates</span><strong>November 2-5, 2026</strong></div>
        <div class="summary-item"><span>City</span><strong>Puerto Varas, Chile</strong></div>
        <div class="summary-item"><span>Venue</span><strong>Hotel Bellavista</strong></div>
        <div class="summary-item"><span>Focus</span><strong>Hantavirus science and Andes Virus workshop</strong></div>
      </section>
      <section class="section intro-band">
        <div class="section-shell ich-story">
          <div class="section-heading reveal">
            <p class="eyebrow">Venue & Location</p>
            <h2>Puerto Varas, located in the scenic Lake District in Southern Chile.</h2>
          </div>
          <div class="prose reveal">
            <p>The 2026 meeting of the International Society for Hantaviruses will take place in Puerto Varas, located in the scenic Lake District in Southern Chile widely regarded as a gateway to Patagonia. The city sits at the foot of the iconic Osorno Volcano in southern Chile, providing a spectacular natural setting for scientific exchange and collaboration.</p>
            <p>The conference will bring together scientists and health professionals from around the world to share and discuss the latest advances across a broad range of topics, including viral epidemiology, ecology, virus-host interactions, pathogenesis, clinical aspects of disease, and the development of vaccines and therapeutics.</p>
          </div>
        </div>
      </section>
      <section class="section data-section">
        <div class="section-shell">
          <div class="section-heading compact reveal">
            <p class="eyebrow">Scientific Program & Keynote Speakers</p>
            <h2>An excellent platform for students, postdoctoral researchers, and established scientists.</h2>
            <p>The International Conference on Hantaviruses will provide an excellent platform for students, postdoctoral researchers, and established scientists to present their latest findings and engage with the international hantavirus research community. In addition, the organizing committee has invited leading experts in the field to deliver keynote lectures highlighting cutting-edge developments in hantavirus research.</p>
          </div>
        </div>
      </section>
      <section class="section intro-band">
        {location_carousel(prefix)}
      </section>
      {committee_directory_section(prefix, "committees")}
      <section class="section ich-workshop">
        <div class="section-shell ich-workshop-layout">
          <div class="section-heading reveal">
            <p class="eyebrow">Specialized Workshop: Andes Virus</p>
            <h2>A one-day workshop dedicated to Andes virus.</h2>
          </div>
          <div class="prose reveal">
            <p>In addition to the traditional ICH scientific program, the conference will feature on November 5 a one-day workshop dedicated to Andes virus, a pathogen of particular regional importance. This workshop will provide an opportunity for researchers, clinicians, and public health professionals to discuss the local epidemiology, clinical management, and public health response to hantavirus cardiopulmonary syndrome.</p>
            <p>Local authorities and decision-makers will also be invited to participate, fostering dialogue between the scientific community and public health stakeholders.</p>
            <a class="button button-primary" href="{local(prefix, "ich2026/programme/")}">Workshop programme</a>
          </div>
        </div>
      </section>
      <section class="section intro-band">
        <div class="section-shell contact-layout">
          <div class="section-heading reveal">
            <p class="eyebrow">Partners & Sponsors</p>
            <h2>Institutions and sponsors supporting the Puerto Varas meeting.</h2>
          </div>
          <div class="contact-actions reveal">
            <a class="button button-primary" href="{local(prefix, "ich2026/partners-sponsors/")}">View partners & sponsors</a>
          </div>
        </div>
      </section>"""


def organizing_committees_page(prefix: str) -> str:
    crumbs = [("Home", local(prefix)), ("ICH2026", local(prefix, "ich2026/")), ("Committees", None)]
    return f"""
      {page_hero(prefix, "ICH2026 Committees", "Organizing Committees", "Scientific and local teams coordinating ICH2026 in Puerto Varas.", "ich2026/from-zip/pvaras2.jpg", [("Partners & sponsors", local(prefix, "ich2026/partners-sponsors/"), "button-primary"), ("Programme", local(prefix, "ich2026/programme/"), "button-secondary")], breadcrumbs=crumbs)}
      {committee_directory_section(prefix)}"""


def keynote_page(prefix: str) -> str:
    crumbs = [("Home", local(prefix)), ("ICH2026", local(prefix, "ich2026/")), ("Keynote Speakers", None)]
    return f"""
      {page_hero(prefix, "Keynote speakers", "ICH2026 Keynote Speakers", "Invited experts presenting clinical, virological and countermeasure perspectives for ICH2026.", "ich2026/conference-volcano.jpg", breadcrumbs=crumbs)}
      <section class="section speakers">
        <div class="section-shell speaker-grid">
          <article class="speaker reveal">
            {responsive_image(prefix, "speakers/marcela-ferres.png", "Dr. Marcela Ferres", loading="lazy", decoding="async", sizes="196px")}
            <div>
              <h2>Dr. Marcela Ferres</h2>
              <p class="speaker-meta">Pontificia Universidad Catolica, Chile</p>
              <p>Dr. Marcela Ferres is a professor, pediatric infectious diseases specialist, and director of the Infectious Diseases and Molecular Virology Laboratory at the Faculty of Medicine, Universidad Catolica de Chile, and Red de Salud UC CHRISTUS in Santiago.</p>
              <p>Her hantavirus research focuses on the epidemiological, cellular and molecular factors involved in person-to-person transmission of Andes virus. Her work has contributed to studies on transmission risks, early diagnostic methods and viral detection in different body fluids.</p>
              <p>Dr. Ferres has authored more than 30 peer-reviewed publications in hantavirus, SARS-CoV-2 and diagnostic virology, and is the author of a Clinical Virology book currently in preparation for its third edition.</p>
              <a class="text-link" href="https://orcid.org/0000-0001-9415-4657" target="_blank" rel="noreferrer">ORCID profile</a>
            </div>
          </article>
          <article class="speaker reveal">
            {responsive_image(prefix, "speakers/jay-hooper.png", "Dr. Jay Hooper", loading="lazy", decoding="async", sizes="196px")}
            <div>
              <h2>Dr. Jay Hooper</h2>
              <p class="speaker-meta">United States Army Medical Research Institute of Infectious Diseases (USAMRIID), USA</p>
              <p>Dr. Jay Hooper is Chief of the Molecular Virology Branch at USAMRIID. His work focuses on the discovery and development of medical countermeasures against high-consequence viral diseases, including hemorrhagic fevers and diseases caused by poxviruses.</p>
              <p>He has more than 30 years of research experience with lethal viruses, largely in BSL-3 and BSL-4 high-containment settings. Dr. Hooper received a B.A. in Biology from Colby College and a Ph.D. in Virology from Harvard University; his research has produced more than 100 peer-reviewed publications and 15 patents.</p>
              <a class="text-link" href="https://orcid.org/0000-0002-4475-0415" target="_blank" rel="noreferrer">ORCID profile</a>
            </div>
          </article>
        </div>
      </section>"""


def programme_page(prefix: str) -> str:
    crumbs = [("Home", local(prefix)), ("ICH2026", local(prefix, "ich2026/")), ("Programme", None)]
    return f"""
      {page_hero(prefix, "ICH2026 Program", "International Hantavirus Conference", "November 2-4, followed by the Andes Virus Workshop on November 5.", "ich2026/ich2026-logo-landscape.png", [("Registration", local(prefix, "ich2026/abstracts-registration/"), "button-primary")], breadcrumbs=crumbs)}
      <section class="section program">
        <div class="section-shell">
          <div class="program-intro reveal">
            <p class="eyebrow">Programme overview</p>
            <h2>Scientific sessions and a focused Andes Virus Workshop.</h2>
            <p>The programme separates the main conference themes from the workshop day, keeping topics easy to scan for researchers, clinicians and public-health teams.</p>
          </div>
          <div class="program-grid program-support">
            <article class="program-track reveal"><p class="track-date">November 2-4</p><h3>International Hantavirus Conference</h3><p>The meeting will cover the following topics:</p><ul><li>Viral epidemiology, evolution &amp; genetics</li><li>Virus ecology and climate change</li><li>Viral replication</li><li>Virus-host interactions</li><li>Pathogenesis</li><li>Vaccines &amp; therapeutics</li><li>Clinical aspects &amp; diagnostics</li></ul></article>
            <article class="program-track highlight reveal"><p class="track-date">November 5</p><h3>Andes Virus Workshop</h3><p>Topics will cover the following aspects:</p><ul><li>Translation of vaccine &amp; therapeutics candidates</li><li>Early diagnosis</li><li>Management of Andes virus-exposed persons</li><li>Surveillance of Andes virus</li><li>Regional Network</li><li>Other topics</li><li>Round Table discussion</li></ul><p class="track-note">This workshop will be conducted with simultaneous translation (English-Spanish; Spanish-English).</p></article>
          </div>
        </div>
      </section>"""


def registration_page(prefix: str) -> str:
    crumbs = [("Home", local(prefix)), ("ICH2026", local(prefix, "ich2026/")), ("Abstracts & Registration", None)]
    return f"""
      {page_hero(prefix, "ICH2026 Registration & Abstract Submission", "Registration and abstract submission.", "Abstract submission opens in May 2026, with early bird registration planned for May-July.", "venue/puerto-varas-waterfront.jpg", [("Conference form", CONFERENCE_FORM, "button-primary"), ("Contact", contact_href(prefix), "button-secondary")], breadcrumbs=crumbs)}
      <section class="section intro-band">
        <div class="section-shell registration-flow-layout">
          <div class="section-heading reveal"><p class="eyebrow">Registration flow</p><h2>ICH2026 Registration & Abstract Submission</h2><p>Comming soon ...</p><p>We apologize for the delay. Our team is currently supporting the cruise ship emergency.</p></div>
          <div class="registration-flow">
            <article class="registration-item reveal"><span>Abstract Submission</span><strong>Opening May 2026</strong><a class="text-link" href="{CONFERENCE_FORM}" target="_blank" rel="noreferrer">Link</a></article>
            <article class="registration-item reveal"><span>Early Bird Registration</span><strong>May - July</strong><a class="text-link" href="{CONFERENCE_FORM}" target="_blank" rel="noreferrer">Link</a></article>
            <article class="registration-item reveal"><span>Standar Registration</span><strong>August - October</strong><a class="text-link" href="{CONFERENCE_FORM}" target="_blank" rel="noreferrer">Link</a></article>
          </div>
        </div>
      </section>"""


def venue_page(prefix: str) -> str:
    links = "".join(travel_link_card(icon, label, description, href) for icon, label, description, href in TRAVEL_LINKS)
    crumbs = [("Home", local(prefix)), ("ICH2026", local(prefix, "ich2026/")), ("Venue & Travel", None)]
    return f"""
      {page_hero(prefix, "ICH2026 Venue & Travel", "Hotel Bellavista, Puerto Varas.", "The 2026 meeting will take place in the Hotel Bellavista, Puerto Varas.", "venue/hotel-bellavista-window.jpg", [("Open map", "https://goo.gl/maps/dv2jUC4hSGLvr2Ld9", "button-primary"), ("Hotel Bellavista", "https://hotelbellavista.cl/reuniones-y-eventos-corporativos-2/", "button-secondary")], breadcrumbs=crumbs)}
      <section class="section venue">
        <div class="section-shell venue-layout">
          <div class="venue-copy reveal">
            <p class="eyebrow">How to get to Puerto Varas</p>
            <h2>A practical route into the Chilean Lake District.</h2>
            <div class="venue-address">
              <span>Venue address</span>
              <a href="https://goo.gl/maps/dv2jUC4hSGLvr2Ld9" target="_blank" rel="noreferrer">Av. Vicente Perez Rosales #060, Puerto Varas</a>
            </div>
            <div class="travel-steps">
              <div><span>Arrival</span><strong>Santiago (SCL)</strong><small>Immigration, luggage and domestic connection.</small></div>
              <div><span>Connection</span><strong>Puerto Montt (PMC)</strong><small>Domestic flight to El Tepual Airport.</small></div>
              <div><span>Transfer</span><strong>Puerto Varas</strong><small>Private transfer, taxi, bus or shuttle to the venue.</small></div>
            </div>
            <div class="travel-shortcuts" aria-label="Priority travel resources">
              <a href="https://www.survip.cl/transfer-aeropuerto-puerto-montt-a-puerto-varas.php" target="_blank" rel="noreferrer">{travel_icon("car")}<span><strong>Puerto Montt to Puerto Varas</strong><small>Survip transfer from El Tepual Airport (PMC) to Puerto Varas.</small></span></a>
              <a href="https://ww2.trasladoaeropuerto.cl/" target="_blank" rel="noreferrer">{travel_icon("plane")}<span><strong>Santiago SCL stop-over</strong><small>Transfer service for participants staying overnight near Santiago airport.</small></span></a>
            </div>
          </div>
          <figure class="venue-image reveal">{responsive_image(prefix, "venue/puerto-varas-waterfront.jpg", "Hotel Bellavista conference room", loading="lazy", decoding="async", sizes="(max-width: 1060px) 100vw, 520px")}<figcaption>Hotel Bellavista conference facilities</figcaption></figure>
        </div>
      </section>
      <section class="section hotel-planning">
        <div class="section-shell hotel-planning-layout">
          <div class="section-heading reveal">
            <p class="eyebrow">Hotels</p>
            <h2>Accommodation information will be incorporated as it is confirmed.</h2>
          </div>
          <div class="hotel-planning-list reveal" aria-label="Hotel information status">
            <article>
              <span>Puerto Varas</span>
              <h3>Conference-area hotels</h3>
              <p>A curated list of hotels near Hotel Bellavista and central Puerto Varas will be added after confirmation by the organizing team.</p>
            </article>
            <article>
              <span>Santiago airport</span>
              <h3>Stop-over hotels</h3>
              <p>Recommended hotels near Arturo Merino Benitez International Airport (SCL) will be added for participants who need an overnight connection before flying to Puerto Montt.</p>
            </article>
          </div>
        </div>
      </section>
      <section class="section intro-band">
        <div class="section-shell travel-detail-list">
          <article class="reveal">
            <p class="eyebrow">International arrival</p>
            <h2>Arrive through Santiago (SCL)</h2>
            <p>Most international travelers will arrive at Arturo Merino Benítez International Airport (SCL) in Santiago, Chile.</p>
            <h3>After landing</h3>
            <ul><li>Proceed through immigration and customs</li><li>Collect your luggage</li><li>Follow signs for domestic connections</li></ul>
            <p><strong>Tip:</strong> Allow at least 2-3 hours for connection time, especially if arriving from long-haul international flights.</p>
            <p>Alternatively, you may prefer to make a stop-over in Santiago. The Santiago transfer contact below is for SCL airport transfers and can be useful for overnight stays before the domestic flight to Puerto Montt. A curated list of hotels near Santiago airport will be added once confirmed by the organizing team. It is also possible to book <a class="text-link" href="https://www.tripadvisor.com/Attractions-g294305-Activities-c42-t205-Santiago_Santiago_Metropolitan_Region.html" target="_blank" rel="noreferrer">day trips</a> to diverse destinations, close to, or in <a class="text-link" href="https://www.viator.com/Santiago/d713?pid=P00095352&mcid=42383&medium=link&campaign=scltours" target="_blank" rel="noreferrer">Santiago</a>.</p>
          </article>
          <article class="reveal">
            <p class="eyebrow">Domestic connection</p>
            <h2>Fly from Santiago to Puerto Montt (PMC)</h2>
            <p>From Santiago, take a domestic flight to El Tepual Airport (PMC) in Puerto Montt.</p>
            <ul><li>Flight duration: approximately 1 hour 40 minutes</li><li>Airlines operate multiple daily flights</li></ul>
            <p><strong>Tip:</strong> Puerto Montt is the main gateway to the Los Lagos region and Puerto Varas.</p>
          </article>
          <article class="reveal">
            <p class="eyebrow">Airport transfer</p>
            <h2>Connect from Puerto Montt Airport to Puerto Varas</h2>
            <p>Puerto Varas is located approximately 20-30 km from the airport, with a travel time of about 25-30 minutes depending on traffic.</p>
            <p>Upon arrival at the airport, you will find several transportation options.</p>
            <h3>Private or Shared Transfer</h3>
            <ul><li>Pre-booked or available at the airport</li><li>Drop-off directly at your hotel</li><li>Travel time: ~30 minutes</li><li>Approximate amount: 15-25 USD</li></ul>
            <p>For the Puerto Montt to Puerto Varas route, participants can review the <a class="text-link" href="https://www.survip.cl/transfer-aeropuerto-puerto-montt-a-puerto-varas.php" target="_blank" rel="noreferrer">Survip transfer</a>. For participants spending a night in Santiago, the SCL transfer service is available through <a class="text-link" href="https://ww2.trasladoaeropuerto.cl/" target="_blank" rel="noreferrer">Airport Transfer</a>, <a class="text-link" href="https://api.whatsapp.com/send?phone=56976053701&text=hola,%20lo%20contacto%20desde%20la%20p%C3%A1gina%20web" target="_blank" rel="noreferrer">WhatsApp +56976053701</a>, or <a class="text-link" href="mailto:reservas@trasladoaeropuerto.cl">reservas@trasladoaeropuerto.cl</a>.</p>
            <h3>Taxi</h3>
            <ul><li>Available directly outside the terminal</li><li>Travel time: ~25-30 minutes</li><li>Safe and widely used</li><li>Estimated cost: 20-30 USD</li></ul>
            <h3>Bus / Shuttle</h3>
            <ul><li>Budget-friendly option</li><li>Travel time: ~30-40 minutes depending on route</li><li>Estimated cost: 2 USD</li><li>Departures from Puerto Montt bus terminal</li></ul>
            <p>Taxis and transfers are the most convenient options for international travelers.</p>
          </article>
          <article class="reveal">
            <p class="eyebrow">Final destination</p>
            <h2>Puerto Varas</h2>
            <p>Puerto Varas is a scenic lakeside city located in southern Chile, known for:</p>
            <ul><li>Lake Llanquihue</li><li>Osorno Volcano</li><li>Easy access to national parks and research sites</li></ul>
            <h3>Travel Tips</h3>
            <ul><li>Currency: Chilean Peso (CLP)</li><li>Most taxis and services accept cards, but carrying some cash is recommended</li><li>Weather can change quickly - bring appropriate clothing</li><li>Spanish is the local language, but basic English is commonly understood in tourism services</li></ul>
          </article>
        </div>
      </section>
      <section class="section data-section">
        <div class="section-shell"><div class="section-heading compact reveal"><p class="eyebrow">Travel resources</p><h2>Venue, airport and transfer contacts for ICH2026 participants.</h2></div><div class="travel-link-list reveal">{links}</div></div>
      </section>"""


def sponsors_page(prefix: str) -> str:
    groups = []
    for category, label in SPONSOR_GROUP_LABELS:
        cards = "".join(
            f'<a class="sponsor reveal" href="{href}" target="_blank" rel="noreferrer">{responsive_image(prefix, image, name, loading="lazy", decoding="async", sizes="360px")}<span>{escape(name)}</span></a>'
            for item_category, name, href, image in SPONSORS
            if item_category == category
        )
        groups.append(
            f"""
            <section class="sponsor-group" aria-labelledby="sponsor-group-{escape(category.lower().replace(" ", "-").replace("&", "and"))}">
              <div class="sponsor-group-heading reveal">
                <h2 id="sponsor-group-{escape(category.lower().replace(" ", "-").replace("&", "and"))}">{escape(category)}</h2>
              </div>
              <div class="sponsor-grid" role="list">{cards}</div>
            </section>"""
        )
    crumbs = [("Home", local(prefix)), ("ICH2026", local(prefix, "ich2026/")), ("Partners & Sponsors", None)]
    return f"""
      {page_hero(prefix, "Partners & sponsors", "ICH2026 partners and sponsors.", "Organizations supporting the ICH2026 scientific meeting in Puerto Varas, Chile.", "ich2026/pto-varas2.png", breadcrumbs=crumbs)}
      <section class="section sponsors"><div class="section-shell sponsors-layout">{"".join(groups)}</div></section>"""


def archive_cell(prefix: str, label: str, href: str, *, is_image: bool = False, caption: str = "") -> str:
    if href:
        target_href = img(prefix, href) if is_image else local(prefix, href)
        if is_image:
            image_caption = caption or label
            return (
                f'<a class="archive-link" href="{target_href}" data-lightbox-src="{target_href}" '
                f'data-lightbox-caption="{escape(image_caption)}">{escape(label)}</a>'
            )
        return f'<a class="archive-link" href="{target_href}" target="_blank" rel="noreferrer">{escape(label)}</a>'
    return '<span class="archive-muted">-</span>'


def abstract_book_link(prefix: str, label: str, href: str) -> str:
    if not href:
        return ""
    icon = (
        '<span class="archive-abstract-icon" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M7 3h7l4 4v14H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/>'
        '<path d="M14 3v5h5"/>'
        '<path d="M8.5 13h7"/>'
        '<path d="M8.5 16h5"/>'
        '</svg></span>'
    )
    return (
        f'<a class="archive-abstract-link" href="{local(prefix, href)}" target="_blank" rel="noreferrer">'
        f'{icon}<span>{escape(label or "Abstract Book")}</span></a>'
    )


def former_images_for_year(year: str) -> list[str]:
    for _, gallery_year, _, images in FORMER_GALLERIES:
        if gallery_year == year:
            return images
    return []


def timeline_abstract_link(prefix: str, label: str, href: str) -> str:
    if not href:
        return ""
    return (
        f'<a class="archive-timeline-abstract" href="{local(prefix, href)}" target="_blank" rel="noreferrer" '
        f'aria-label="{escape(label or "Abstract Book")}">'
        '<span class="archive-timeline-abstract-icon" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M7 3h7l4 4v14H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/>'
        '<path d="M14 3v5h5"/><path d="M8.5 13h7"/><path d="M8.5 16h5"/>'
        '</svg></span><span>Abstract</span></a>'
    )


def former_meetings_timeline(prefix: str) -> str:
    items = []
    timeline_entries = list(
        reversed(
            [
                (number, year, location, abstract_label, abstract_href, False)
                for number, year, location, abstract_label, abstract_href, *_ in FORMER_MEETINGS
            ]
        )
    )
    timeline_entries.append(("XIII", "2026", "Puerto Varas, Chile", "", "", True))
    for index, (number, year, location, abstract_label, abstract_href, is_upcoming) in enumerate(timeline_entries):
        item_class = "archive-timeline-item is-upcoming" if is_upcoming else "archive-timeline-item"
        timeline_tag = '<span class="archive-timeline-tag">Next ICH</span>' if is_upcoming else ""
        abstract_html = timeline_abstract_link(prefix, abstract_label, abstract_href)
        items.append(
            f"""
            <li class="{item_class}" style="--timeline-index: {index}">
              <div class="archive-timeline-card">
                {timeline_tag}
                <span class="archive-timeline-no">{escape(number)}</span>
                <time class="archive-timeline-year" datetime="{escape(year)}">{escape(year)}</time>
                <strong class="archive-timeline-location">{escape(location)}</strong>
                {abstract_html}
              </div>
            </li>"""
        )
    return f"""
      <div class="archive-timeline-wrap reveal">
        <ol class="archive-timeline" aria-label="International Hantavirus Conference timeline">
          {"".join(items)}
        </ol>
      </div>"""


def former_meeting_materials(prefix: str) -> str:
    cards = []
    meeting_lookup = {year: (abstract_label, abstract_href) for _, year, _, abstract_label, abstract_href, _, _ in FORMER_MEETINGS}
    for number, year, location, images in FORMER_GALLERIES:
        abstract_label, abstract_href = meeting_lookup.get(year, ("Abstract Book", ""))
        if not images and not abstract_href:
            continue
        lead = images[0] if images else "ui/society-archive-2.png"
        photo_count = len(images)
        gallery_id = f"former-{year}"
        gallery_links = []
        for index, asset in enumerate(images, start=1):
            caption = f"ICH {year} | {location} | Photo {index} of {photo_count}"
            lightbox_src = optimized_image_url(prefix, asset)
            gallery_links.append(
                f'<a class="archive-hidden-lightbox" href="{img(prefix, asset)}" '
                f'data-lightbox-src="{lightbox_src}" data-lightbox-full-src="{img(prefix, asset)}" data-lightbox-group="{escape(gallery_id)}" '
                f'data-lightbox-caption="{escape(caption)}" data-lightbox-alt="{escape(f"ICH {year} {location} photo {index}")}" tabindex="-1" aria-hidden="true">Photo {index}</a>'
            )
        hidden_gallery = "".join(gallery_links[1:])
        lead_caption = f"ICH {year} | {location} | Photo 1 of {photo_count}"
        photo_label = f"{photo_count} photo" if photo_count == 1 else f"{photo_count} photos"
        materials_label = f"{escape(number)} | {escape(year)}"
        lead_lightbox_src = optimized_image_url(prefix, lead)
        cards.append(
            f"""
            <article class="archive-material reveal">
              <a class="archive-material-image" href="{img(prefix, lead)}" data-lightbox-src="{lead_lightbox_src}" data-lightbox-full-src="{img(prefix, lead)}" data-lightbox-group="{escape(gallery_id)}" data-lightbox-caption="{escape(lead_caption)}" aria-label="Open {escape(photo_label)} from ICH {escape(year)} in {escape(location)}">
                {responsive_image(prefix, lead, f"ICH {year} {location}", loading="lazy", decoding="async", sizes="(max-width: 780px) 92vw, 560px")}
                <span class="archive-photo-count">{escape(photo_label)}</span>
                <span class="archive-gallery-label">View gallery</span>
              </a>
              <div class="archive-material-copy">
                <span>{materials_label}</span>
                <h3>{escape(location)}</h3>
                {abstract_book_link(prefix, abstract_label or "Abstract Book", abstract_href)}
                {hidden_gallery}
              </div>
            </article>"""
        )
    return f'<div class="archive-material-grid">{"".join(cards)}</div>'


def former_meetings_page(prefix: str) -> str:
    return (
        f"""
      {page_hero(prefix, "Society archive", "Former Meetings", "A concise archive of International Hantavirus Conference milestones.", "former-meetings/2023-seoul-2.jpg", [("ICH2026", local(prefix, "ich2026/"), "button-primary")])}
      <section class="section intro-band">
        <div class="section-shell two-column">
          <div class="section-heading reveal">
            <p class="eyebrow">International meetings</p>
            <h2>Triennial exchange across hantavirus research communities.</h2>
          </div>
          <div class="prose reveal">
            <p>The International Society for Hantaviruses was founded in 1989 with its first meeting in Seoul, Korea. This archive now includes photo and abstract-book material recovered from the Webpage asset package.</p>
          </div>
        </div>
        <div class="section-shell archive-awards reveal">
          <p class="eyebrow">Lectureship awards</p>
          <div>
            <h2>Two lectureship awards frame the scientific legacy of each triennial ICH.</h2>
            <p>At each triennial ICH, the Ho-Wang Lee Lifetime Achievement Award recognizes a senior hantavirologist for exceptional contributions to hantavirus research, while the Joel M. Dalrymple Memorial Award honors an early- to mid-career researcher whose innovative and forward-looking work reflects the legacy of Dr. Dalrymple at the U.S. Army Medical Research Institute of Infectious Diseases.</p>
          </div>
        </div>
      </section>"""
        f"""
      <section class="section data-section">
        <div class="section-shell">
          <div class="section-heading compact reveal">
            <p class="eyebrow">Conference timeline</p>
            <h2>International Hantavirus Conference editions, 1989-2026.</h2>
          </div>
          {former_meetings_timeline(prefix)}
        </div>
      </section>
      <section class="section intro-band">
        <div class="section-shell">
          <div class="section-heading compact reveal">
            <p class="eyebrow">Photos & abstracts</p>
            <h2>Available visual records and abstract books.</h2>
          </div>
          {former_meeting_materials(prefix)}
        </div>
      </section>"""
    )


def communications_page(prefix: str) -> str:
    who_event = "https://www.who.int/news-room/events/detail/2026/05/15/default-calendar/emergency-scientific-consultation-on-andes-virus-medical-countermeasures-(mcm)-r-d"
    who_focus = "https://www.who.int/news-room/events/detail/2026/05/20/default-calendar/hantavirus-in-focus-i-what-we-know-and-what-it-means"
    statement_href = "https://zenodo.org/records/20298312"
    news_items = [
        {
            "category": "ISH statement",
            "date": "May 19, 2026",
            "title": "Andes virus transmission and current outbreak investigation",
            "description": "Statement from ISH and members of the international hantavirus research and clinical community, linked to the Zenodo record supplied by the team.",
            "href": statement_href,
            "external": True,
            "label": "Open Zenodo record",
        },
        {
            "category": "WHO guidance",
            "date": "May 15, 2026",
            "title": "Laboratory testing of Andes virus infection",
            "description": "WHO interim guidance for laboratory testing of Andes virus infection.",
            "href": "https://www.who.int/publications/i/item/B09765",
            "external": True,
            "label": "Read WHO guidance",
        },
        {
            "category": "ECDC update",
            "date": "May 2026",
            "title": "Andes hantavirus outbreak in cruise ship",
            "description": "ECDC epidemiological update and associated guidance for the Andes hantavirus outbreak.",
            "href": "https://www.ecdc.europa.eu/en/infectious-disease-topics/hantavirus-infection/surveillance-and-updates/andes-hantavirus-outbreak",
            "external": True,
            "label": "View ECDC update",
        },
        {
            "category": "WHO webinar",
            "date": "May 20, 2026",
            "title": "Hantavirus in Focus I: what we know and what it means",
            "description": "WHO EPI-WIN webinar on the current multi-country hantavirus event, public-health implications and community protection.",
            "href": who_focus,
            "external": True,
            "label": "View WHO webinar",
        },
        {
            "category": "WHO R&D Blueprint",
            "date": "WHO",
            "title": "R&D Blueprint for epidemics",
            "description": "WHO programme for rapid activation of research and development during epidemics, including the Andes virus MCM R&D consultation.",
            "href": "https://www.who.int/teams/blueprint",
            "external": True,
            "label": "Open WHO Blueprint",
        },
        {
            "category": "WHO consultation",
            "date": "May 15, 2026",
            "title": "Emergency scientific consultation on Andes virus MCM R&D",
            "description": "WHO convened an emergency scientific consultation on Andes virus medical countermeasures. Session 1 was chaired by Nicole Tischler.",
            "href": who_event,
            "external": True,
            "label": "View WHO event",
        },
        {
            "category": "Public-health resource",
            "date": "WHO",
            "title": "WHO hantavirus health topic",
            "description": "A reference point for public-health context, disease information and international guidance.",
            "href": "https://www.who.int/health-topics/hantavirus#tab=tab_1",
            "external": True,
            "label": "Read WHO topic",
        },
        {
            "category": "Webinar",
            "date": "PHA4GE",
            "title": "Hantavirus and genomic epidemiology",
            "description": "A scientific webinar focused on sequencing, genomic epidemiology and implementation questions for hantavirus surveillance.",
            "href": "https://pha4ge.org/webinars/hantavirus-and-genomic-epidemiology-has-it-been-smooth-sailing/",
            "external": True,
            "label": "Watch webinar",
        },
    ]
    lead_item = news_items[0]
    secondary_items = news_items[1:]
    news_cards = []
    for item in secondary_items:
        target = ' target="_blank" rel="noreferrer"' if item["external"] else ""
        card_class = "news-card reveal"
        news_cards.append(
            f"""
            <a class="{card_class}" href="{item["href"]}"{target}>
              <span class="news-card-type">{escape(item["category"])}</span>
              <span class="news-card-date">{escape(item["date"])}</span>
              <h3>{escape(item["title"])}</h3>
              <p>{escape(item["description"])}</p>
              <strong>{escape(item["label"])}</strong>
            </a>"""
        )
    return f"""
      {page_hero(prefix, "Society communications", "Communications", "Statements, public-health resources and scientific exchange updates.", "ich2026/hantavirus-em.jpg")}
      <section class="section intro-band newsroom">
        <div class="section-shell news-lead-single">
          <article class="news-lead-card reveal">
            <div class="news-kicker"><span>{escape(lead_item["category"])}</span><time>{escape(lead_item["date"])}</time></div>
            <h2>{escape(lead_item["title"])}</h2>
            <p>{escape(lead_item["description"])}</p>
            <a class="button button-primary" href="{lead_item["href"]}" target="_blank" rel="noreferrer">{escape(lead_item["label"])}</a>
          </article>
        </div>
      </section>
      <section class="section news-updates">
        <div class="section-shell two-column news-section-heading">
          <div class="section-heading reveal">
            <p class="eyebrow">Latest updates</p>
            <h2>Verified resources for the hantavirus community.</h2>
          </div>
        </div>
        <div class="section-shell news-grid" role="list">{"".join(news_cards)}</div>
      </section>"""


def contact_section() -> str:
    return f"""
      <section class="section contact" id="contact">
        <div class="section-shell contact-layout">
          <div class="section-heading reveal"><p class="eyebrow">Contact</p><h2>Institutional and ICH2026 contacts</h2></div>
          <div class="contact-actions reveal">
            <a class="contact-email" href="mailto:ish@hantavirussociety.org">ISH: ish@hantavirussociety.org</a>
            <a class="contact-email" href="mailto:ICH2026@hantavirussociety.org">ICH2026: ICH2026@hantavirussociety.org</a>
          </div>
        </div>
      </section>"""


def contact_page(prefix: str) -> str:
    return contact_section()


def about_page(prefix: str) -> str:
    return f"""
      {page_hero(prefix, "About ISH", "About the International Society for Hantaviruses", "Founded in 1989 with its first Meeting in Seoul (Korea).", "ui/home-science-hero.webp?v=virus-fill-20260521", [("Apply for ISH Membership", MEMBERSHIP_FORM, "button-primary")])}
      <section class="section intro-band">
        <div class="section-shell about-logo-card reveal">
          {responsive_image(prefix, "ui/logo.png", "International Society for Hantaviruses logo", loading="lazy", decoding="async", sizes="190px")}
          <div>
            <span>International Society for Hantaviruses</span>
          </div>
        </div>
        <div class="section-shell two-column">
          <div class="section-heading reveal">
            <p class="eyebrow">About ISH</p>
            <h2>About the International Society for Hantaviruses</h2>
          </div>
          <div class="prose reveal">
            <p>This society was founded in 1989 with its first Meeting in Seoul (Korea), to promote the advancement and promulgation of knowledge on hantaviruses and the diseases they cause. It also fosters collaboration and the exchange of expertise in all areas of knowledge, including viral epidemiology and ecology, viral replication, host interactions, pathogenesis, advances in vaccine and therapeutics, diagnostics and clinical management.</p>
            <p>The society is led by an International Advisory Board composed of members from countries most affected by hantaviruses, reflecting its global scope and commitment to addressing regional challenges. Since its establishment, the society has convened a triennial meeting that brings together researchers, clinicians, and public health professionals. The next International Hantavirus Conference (ICH) will be held in November 2026 in Puerto Varas, Chile.</p>
            <a class="button button-primary" href="{MEMBERSHIP_FORM}" target="_blank" rel="noreferrer">Apply for ISH Membership</a>
          </div>
        </div>
        <div class="section-shell society-gallery single-image" aria-label="ICH2023 Seoul">
          <figure class="reveal">
            {responsive_image(prefix, "ui/society-archive-2.png", "ICH2023 Seoul meeting participants", loading="lazy", decoding="async", sizes="(max-width: 780px) 100vw, 1180px")}
            <figcaption>ICH2023 Seoul | Republic of Korea</figcaption>
          </figure>
        </div>
      </section>
      <section class="section committees">
        <div class="section-shell">
          <div class="section-heading compact reveal">
            <p class="eyebrow">International Advisory Board</p>
            <h2>Global advisory leadership across hantavirus-affected regions.</h2>
          </div>
          {advisory_grid(prefix)}
        </div>
      </section>
      {contact_section()}"""


PAGES = [
    ("index.html", "home", "International Society for Hantaviruses", "International Society for Hantaviruses and ICH2026 in Puerto Varas, Chile.", home_page),
    ("about-ish/index.html", "about", "About ISH | International Society for Hantaviruses", "About the International Society for Hantaviruses.", about_page),
    ("former-meetings/index.html", "former", "Former Meetings | International Society for Hantaviruses", "Former International Hantavirus Conference meetings.", former_meetings_page),
    ("communications/index.html", "communications", "Communications | International Society for Hantaviruses", "Statements and scientific communications from the International Society for Hantaviruses.", communications_page),
    ("ich2026/index.html", "ich2026", "ICH2026 | International Society for Hantaviruses", "International Conference on Hantaviruses 2026 in Puerto Varas, Chile.", ich2026_page),
    ("ich2026/keynote-speakers/index.html", "keynote", "Keynote Speakers | ICH2026", "Keynote speakers for ICH2026.", keynote_page),
    ("ich2026/programme/index.html", "programme", "Programme | ICH2026", "Scientific programme for ICH2026.", programme_page),
    ("ich2026/abstracts-registration/index.html", "registration", "Abstracts & Registration | ICH2026", "Abstract submission and registration for ICH2026.", registration_page),
    ("ich2026/venue/index.html", "venue", "Venue | ICH2026", "Venue and travel information for ICH2026.", venue_page),
    ("ich2026/organizing-committees/index.html", "committees", "Organizing Committees | ICH2026", "Scientific and local organizing committees for ICH2026.", organizing_committees_page),
    ("ich2026/partners-sponsors/index.html", "sponsors", "Partners & Sponsors | ICH2026", "Partners and sponsors for ICH2026.", sponsors_page),
    ("contact/index.html", "contact", "Contact | ICH2026", "Contact the ICH2026 organizing team.", contact_page),
]


def generate_sitemap() -> None:
    urls = []
    priorities = {"home": "1.0", "about": "0.9", "ich2026": "0.9"}
    for out_path, active, *_ in PAGES:
        page_dir = str(Path(out_path).parent)
        loc = SITE_URL + "/" if page_dir == "." else f"{SITE_URL}/{page_dir}/"
        priority = priorities.get(active, "0.8")
        changefreq = "weekly" if active in ("home", "about", "ich2026") else "monthly"
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>{changefreq}</changefreq>\n    <priority>{priority}</priority>\n  </url>"
        )
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(urls)
    sitemap += "\n</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print("sitemap.xml")


def main() -> None:
    minify_static_assets()
    FILE_VERSION_CACHE.clear()
    for out_path, active, title, description, builder in PAGES:
        prefix = prefix_for(out_path)
        html = minify_html(clean_output(doc(out_path, active, title, description, builder(prefix))))
        target = ROOT / out_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        print(out_path)
    generate_sitemap()


if __name__ == "__main__":
    main()
