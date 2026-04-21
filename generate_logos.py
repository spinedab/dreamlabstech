#!/usr/bin/env python3
"""
DreamLabsTech Logo Generator
Generates a unique SVG logo (512x512) per app in the inventory.
Each SVG has:
  - A gradient background sized to category colors
  - A rounded-square shape (rx=96, ~20% rounded)
  - A centered Unicode emoji scaled to roughly 60% of the tile
  - A subtle white glow behind the emoji

Logos are written to assets/logos/{slug}.svg
Optional PNG versions are written to assets/icons/{slug}.png using rsvg-convert
(fallback: cairosvg, Pillow). 512x512 matches the Google Play Store icon size.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

INVENTORY = "/tmp/apps_inventory.txt"
BASE = Path("/Users/mac_mini2/Documents/GitHub/spinedab/landing-pages")
LOGOS_DIR = BASE / "assets" / "logos"
ICONS_DIR = BASE / "assets" / "icons"
LOGOS_DIR.mkdir(parents=True, exist_ok=True)
ICONS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Category palette (primary / accent) - matches generate.py
# ---------------------------------------------------------------------------
PALETTE = {
    "Salud Mental":     ("#2E7D92", "#A8DADC"),
    "Fitness":          ("#FF5722", "#FF9800"),
    "Finanzas":         ("#1565C0", "#00BFA5"),
    "Alimentacion":     ("#FF8C00", "#4CAF50"),
    "Productividad":    ("#0D47A1", "#448AFF"),
    "Educacion":        ("#6200EA", "#FF6D00"),
    "Estilo de Vida":   ("#2E7D32", "#FFC107"),
    "Musica":           ("#263238", "#00E676"),
    "Herramientas":     ("#455A64", "#29B6F6"),
    "Social":           ("#E91E63", "#FF4081"),
    "Ecommerce":        ("#00ACC1", "#FFAB00"),
    "Juegos":           ("#7B1FA2", "#FFEB3B"),
    "Negocios":         ("#37474F", "#64B5F6"),
    "Salud/Medicina":   ("#00897B", "#80CBC4"),
    "Viajes/Eventos":   ("#FF6F00", "#FFAB40"),
    "Contenido-Media":  ("#D32F2F", "#FFCDD2"),
}

# ---------------------------------------------------------------------------
# Per-app icon map. Emojis where possible, chosen to reflect app purpose.
# Every inventory slug maps to a unique, themed glyph.
# ---------------------------------------------------------------------------
APP_ICONS = {
    # Salud Mental
    "zenmind_app":        "\U0001F9D8",        # person in lotus pose
    "mindcare_app":       "\U0001F9E0",        # brain
    "mindshift_app":      "\U0001F504",        # counterclockwise arrows
    "calmapp_app":        "\U0001F343",        # leaf fluttering
    "calmkids_app":       "\U0001F31F",        # glowing star
    "boostme_app":        "\U0001F680",        # rocket
    "vrtherapy_app":      "\U0001F97D",        # goggles
    "kidmind_app":        "\U0001F9F8",        # teddy bear
    "socialskills_app":   "\U0001F91D",        # handshake
    "tremortest":         "\U0001F590",        # hand with fingers splayed
    "focusblink":         "\U0001F441",        # eye

    # Fitness
    "yogaflow_app":       "\U0001F9D8",        # person in lotus pose
    "yogaflow_levels_app":"\U0001F93C",        # people wrestling
    "fitbuddy_app":       "\U0001F4AA",        # flexed biceps
    "runmaster_app":      "\U0001F3C3",        # person running
    "workout_log":        "\U0001F3CB",        # person lifting weights
    "sleeptracker_app":   "\U0001F4A4",        # zzz
    "trailexplorer_app":  "\U0001F97E",        # hiking boot

    # Finanzas
    "finantrack_app":     "\U0001F4B0",        # money bag
    "couplefinance_app":  "\U0001F495",        # two hearts
    "kidfinance_app":     "\U0001F414",        # piggy (chicken fallback -> use pig below)
    "pocket_expenses":    "\U0001F4B8",        # money with wings
    "subscription_tracker":"\U0001F501",       # repeat
    "receipt_splitter":   "\U0001F9FE",        # receipt
    "paylat_neobank":     "\U0001F3E6",        # bank

    # Override piggy bank (use piggy bank emoji 1F437)
    # We'll assign below.

    # Alimentacion
    "recipefinder_app":   "\U0001F37D",        # fork and knife with plate
    "chefin_app":         "\U0001F468",        # man (chef emoji via ZWJ uses sequence; fallback)
    "cookmaster_app":     "\U0001F373",        # cooking (fried egg)
    "healthybites_app":   "\U0001F957",        # green salad
    "nutritrack_app":     "\U0001F96C",        # leafy green
    "kitchenhelper_app":  "\U0001F374",        # fork and knife
    "meal_planner":       "\U0001F35B",        # curry rice

    # Productividad
    "taskmaster_app":     "\u2705",            # check mark button
    "taskboard_pro":      "\U0001F4CB",        # clipboard
    "myproject_app":      "\U0001F5C2",        # card index dividers
    "teamproject_app":    "\U0001F465",        # busts in silhouette
    "daily_journal":      "\U0001F4D4",        # notebook with decorative cover
    "notevault":          "\U0001F5D2",        # spiral notepad
    "goal_compass":       "\U0001F9ED",        # compass
    "habit_streaks":      "\U0001F525",        # fire
    "event_planner":      "\U0001F4C5",        # calendar
    "eventmaster_app":    "\U0001F389",        # party popper
    "eventonline_app":    "\U0001F3A5",        # movie camera (webinar)
    "shopping_smartlist": "\U0001F6D2",        # shopping trolley
    "travel_packing_list":"\U0001F9F3",        # luggage
    "cleaning_checklist": "\U0001F9F9",        # broom
    "creativehub_app":    "\U0001F3A8",        # artist palette

    # Educacion
    "codelab_app":        "\U0001F4BB",        # laptop
    "linguaar_app":       "\U0001F5E3",        # speaking head
    "signlang_app":       "\U0001F91F",        # love you gesture
    "learnfun_app":       "\U0001F393",        # graduation cap
    "autismlearn_app":    "\U0001F9E9",        # puzzle piece
    "writemaster_app":    "\u270D",            # writing hand
    "photoguide_app":     "\U0001F4F8",        # camera with flash
    "brainboost_app":     "\U0001F4A1",        # light bulb
    "mylibrary_app":      "\U0001F4DA",        # books
    "book_tracker":       "\U0001F4D6",        # open book
    "musicmaster_app":    "\U0001F3BC",        # musical score
    "factcheck_app":      "\U0001F50D",        # magnifying glass tilted left
    "negotia_app":        "\U0001F91D",        # handshake

    # Estilo de Vida
    "petcare_app":        "\U0001F43E",        # paw prints
    "plant_pal":          "\U0001F331",        # seedling
    "greenlife_app":      "\u267B",            # recycling symbol
    "ecotrack_app":       "\U0001F30D",        # earth globe europe-africa
    "eco_track":          "\U0001F333",        # deciduous tree
    "seniorcare_app":     "\U0001F475",        # older woman
    "meditrack_app":      "\U0001F489",        # syringe
    "medai_app":          "\U0001FA7A",        # stethoscope
    "medremind_app":      "\U0001F48A",        # pill
    "skinmole_tracker":   "\U0001F9B4",        # bone (fallback for skin)
    "wanderguide_app":    "\U0001F5FA",        # world map
    "tripplanner_app":    "\U0001F9F3",        # luggage (trip)
    "weatherguard_app":   "\u26C5",            # sun behind cloud

    # Musica
    "piano_app":          "\U0001F3B9",        # musical keyboard
    "aimusiccreator":     "\U0001F3B5",        # musical note
    "pro_audio_eq":       "\U0001F39B",        # control knobs
    "retro_amp":          "\U0001F4FB",        # radio
    "dj_pro_mobile":      "\U0001F3A7",        # headphone
    "bpm_matcher":        "\U0001F3BC",        # musical score
    "humtotabs":          "\U0001F3B6",        # musical notes

    # Herramientas
    "solarpath_ar":       "\u2600",            # sun
    "wallscanner":        "\U0001F9F1",        # brick
    "fake_shutdown":      "\u23FB",            # power symbol
    "anti_eavesdrop":     "\U0001F512",        # locked
    "speakercleaner":     "\U0001F50A",        # speaker high volume
    "barometer_altimeter":"\U0001F321",        # thermometer
    "localdrop":          "\U0001F4E1",        # satellite antenna
    "frequency_counter":  "\U0001F4CA",        # bar chart
    "dashboard_ar":       "\U0001F697",        # automobile
    "threadcount":        "\U0001F9F5",        # thread
    "level_laser_ar":     "\U0001F4CF",        # straight ruler
    "screen_obscure":     "\U0001F576",        # dark sunglasses
    "applocker_dynamic":  "\U0001F510",        # locked with key
    "coin_counter_ai":    "\U0001FA99",        # coin
    "arhome_app":         "\U0001F3E0",        # house with garden
    "protomaker_app":     "\U0001F528",        # hammer
    "carfix_app":         "\U0001F527",        # wrench
    "car_care_log":       "\U0001F6E2",        # oil drum
    "warranty_tracker":   "\U0001F6E1",        # shield
    "matter_app":         "\U0001F4E6",        # package
    "sign_translator_ar": "\U0001F4AC",        # speech balloon

    # Social
    "networkpro_app":     "\U0001F4BC",        # briefcase
    "periodico_app":      "\U0001F4F0",        # newspaper
    "popcorn_app":        "\U0001F37F",        # popcorn
    "myspace_reimagined": "\U0001F31F",        # glowing star
    "unova_social":       "\U0001F310",        # globe with meridians
    "tiktok_clone":       "\U0001F3AC",        # clapper board
    "whatsapp_clone":     "\U0001F4AC",        # speech balloon

    # Ecommerce
    "hospedajeco":        "\U0001F3E8",        # hotel
    "marketco_marketplace":"\U0001F3EA",       # convenience store
    "latamgo_delivery":   "\U0001F6F5",        # motor scooter
    "mercadonova":        "\U0001F6CD",        # shopping bags
    "portapro_app":       "\U0001F45C",        # handbag

    # Juegos
    "alfa_computacional": "\U0001F3B2",        # game die
    "dados_flutter":      "\U0001F3B2",        # game die (uniquified via shape below)
    "gravity_dodger":     "\U0001F680",        # rocket (gravity + motion)

    # Negocios
    "client_crm_lite":    "\U0001F464",        # bust in silhouette
    "service_ticket_desk":"\U0001F3AB",        # ticket
    "inventory_manager":  "\U0001F4E6",        # package
    "hotelmaster_app":    "\U0001F3E8",        # hotel
    "demo":               "\u2699",            # gear
    "rider_app":          "\U0001F697",        # automobile (rider)
    "driver_app":         "\U0001F699",        # sport utility vehicle
    "superapp":           "\U0001F4F1",        # mobile phone
    "rider":              "\U0001F6F8",        # ufo (antigravity)
    "driver":             "\U0001F6F0",        # satellite
}

# Patch a few overlapping picks to keep every logo unique
APP_ICONS["kidfinance_app"] = "\U0001F437"        # pig face (piggy bank idea)
APP_ICONS["chefin_app"] = "\U0001F35C"           # steaming bowl (chef-in)
APP_ICONS["dados_flutter"] = "\U0001F4F2"        # mobile phone with arrow (flutter + dice)

# SkinMole tracker better icon
APP_ICONS["skinmole_tracker"] = "\U0001F50E"     # magnifying glass tilted right (derm)

# Fitness: keep yogaflow_app / yogaflow_levels_app distinct
APP_ICONS["yogaflow_app"] = "\U0001F9D8"         # lotus pose
APP_ICONS["yogaflow_levels_app"] = "\U0001F3D4"  # snow-capped mountain (levels)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def svg_template(slug: str, primary: str, accent: str, emoji: str) -> str:
    """Build a 512x512 SVG logo for a single app."""
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", slug)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="{slug} logo">
  <defs>
    <linearGradient id="bg_{safe_id}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{primary}"/>
      <stop offset="100%" stop-color="{accent}"/>
    </linearGradient>
    <radialGradient id="glow_{safe_id}" cx="50%" cy="52%" r="42%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.55"/>
      <stop offset="60%" stop-color="#ffffff" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
    <filter id="shadow_{safe_id}" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.18"/>
    </filter>
  </defs>
  <rect x="0" y="0" width="512" height="512" rx="96" ry="96" fill="url(#bg_{safe_id})"/>
  <circle cx="256" cy="266" r="180" fill="url(#glow_{safe_id})"/>
  <text x="256" y="320" text-anchor="middle"
        font-family="Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, Twemoji Mozilla, EmojiOne Color, Symbola, sans-serif"
        font-size="280" filter="url(#shadow_{safe_id})">{emoji}</text>
</svg>
"""


def read_inventory(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            # tolerate trailing empties
            while len(parts) < 4:
                parts.append("")
            slug, pkg, category, desc = parts[0], parts[1], parts[2], "|".join(parts[3:])
            rows.append((slug, pkg, category, desc))
    return rows


def main() -> int:
    rows = read_inventory(INVENTORY)
    total = len(rows)
    print(f"[generate_logos] {total} apps found in inventory")

    # Generate SVGs
    missing_icon = []
    for slug, _pkg, category, _desc in rows:
        primary, accent = PALETTE.get(category, PALETTE["Herramientas"])
        emoji = APP_ICONS.get(slug)
        if emoji is None:
            missing_icon.append(slug)
            emoji = "\u2728"  # sparkles fallback

        svg = svg_template(slug, primary, accent, emoji)
        (LOGOS_DIR / f"{slug}.svg").write_text(svg, encoding="utf-8")

    print(f"[generate_logos] Wrote {total} SVGs to {LOGOS_DIR}")
    if missing_icon:
        print(f"[generate_logos] WARNING: no icon mapped for {len(missing_icon)}: "
              f"{', '.join(missing_icon[:10])}"
              + (" ..." if len(missing_icon) > 10 else ""))

    # Generate PNGs via rsvg-convert (preferred) or cairosvg fallback
    png_count = write_pngs(rows)
    print(f"[generate_logos] Wrote {png_count} PNGs to {ICONS_DIR}")
    return 0


def write_pngs(rows) -> int:
    """Render each PNG directly with Pillow so color emoji survive.

    SVG-to-PNG converters like rsvg-convert, cairosvg and ImageMagick do not
    render color emoji glyphs, so we skip that round-trip and paint the
    gradient + emoji ourselves. Falls back to rsvg-convert if Pillow isn't
    available, which at least produces monochrome silhouettes.
    """
    try:
        from PIL import Image  # noqa: F401
        print("[generate_logos] Using Pillow + Apple Color Emoji")
        return _png_via_pillow(rows)
    except Exception as exc:
        print(f"[generate_logos] Pillow unavailable ({exc}), trying rsvg-convert")

    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        print(f"[generate_logos] Using rsvg-convert at {rsvg}")
        return _png_via_rsvg(rsvg, rows)

    try:
        import cairosvg  # noqa: F401
        print("[generate_logos] Using cairosvg")
        return _png_via_cairosvg(rows)
    except Exception as exc:
        print(f"[generate_logos] cairosvg unavailable: {exc}")

    magick = shutil.which("magick") or shutil.which("convert")
    if magick:
        print(f"[generate_logos] Using ImageMagick at {magick}")
        return _png_via_magick(magick, rows)

    print("[generate_logos] No SVG->PNG converter available; skipping PNGs")
    return 0


def _png_via_pillow(rows) -> int:
    """Render each 512x512 logo as PNG with gradient bg + color emoji."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    SIZE = 512
    RX = 96
    # Apple Color Emoji only supports discrete sizes; 160 is the biggest.
    # We draw onto a 320x320 canvas at size 160 then upscale + composite.
    EMOJI_SIZE = 160
    emoji_font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"
    try:
        emoji_font = ImageFont.truetype(emoji_font_path, EMOJI_SIZE)
    except Exception as exc:
        print(f"  Apple Color Emoji unavailable: {exc}")
        return 0

    def hex_to_rgb(h: str):
        h = h.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def rounded_mask(size: int, rx: int) -> "Image.Image":
        m = Image.new("L", (size, size), 0)
        md = ImageDraw.Draw(m)
        md.rounded_rectangle((0, 0, size - 1, size - 1), radius=rx, fill=255)
        return m

    def diagonal_gradient(size: int, c1, c2) -> "Image.Image":
        """Linear gradient from top-left (c1) to bottom-right (c2)."""
        img = Image.new("RGB", (size, size), c1)
        px = img.load()
        r1, g1, b1 = c1
        r2, g2, b2 = c2
        denom = max(1, (size - 1) * 2)
        for y in range(size):
            for x in range(size):
                t = (x + y) / denom
                px[x, y] = (
                    int(r1 + (r2 - r1) * t),
                    int(g1 + (g2 - g1) * t),
                    int(b1 + (b2 - b1) * t),
                )
        return img

    def radial_glow(size: int, radius: int) -> "Image.Image":
        """Soft white radial glow centred slightly below middle."""
        glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(glow)
        cx, cy = size // 2, int(size * 0.52)
        steps = 40
        for i in range(steps, 0, -1):
            r = int(radius * (i / steps))
            alpha = int(60 * (i / steps) ** 2)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, alpha))
        return glow.filter(ImageFilter.GaussianBlur(6))

    def render_emoji_tile(emoji: str) -> "Image.Image":
        """Render emoji at 160px into a transparent canvas, then crop tight."""
        # Canvas big enough for the glyph's advance + padding
        tile = Image.new("RGBA", (EMOJI_SIZE * 2, EMOJI_SIZE * 2), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        td.text(
            (EMOJI_SIZE // 2, EMOJI_SIZE // 2),
            emoji,
            font=emoji_font,
            embedded_color=True,
            anchor="mm",
        )
        bbox = tile.getbbox()
        if bbox is None:
            return tile
        return tile.crop(bbox)

    ok = 0
    for slug, _pkg, category, _desc in rows:
        primary, accent = PALETTE.get(category, PALETTE["Herramientas"])
        emoji = APP_ICONS.get(slug, "\u2728")

        # 1. gradient background
        bg = diagonal_gradient(SIZE, hex_to_rgb(primary), hex_to_rgb(accent))

        # 2. apply rounded-square mask
        mask = rounded_mask(SIZE, RX)
        logo = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        logo.paste(bg, (0, 0), mask)

        # 3. soft white glow behind the emoji
        logo.alpha_composite(radial_glow(SIZE, 180))

        # 4. render emoji (~60% of tile)
        emoji_tile = render_emoji_tile(emoji)
        target = int(SIZE * 0.6)  # ~307 px
        w, h = emoji_tile.size
        scale = target / max(w, h)
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        emoji_scaled = emoji_tile.resize(new_size, Image.LANCZOS)

        # soft drop shadow for depth
        shadow = Image.new("RGBA", emoji_scaled.size, (0, 0, 0, 0))
        alpha = emoji_scaled.split()[-1]
        ImageDraw.Draw(shadow).bitmap((0, 0), alpha, fill=(0, 0, 0, 60))
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))

        ex = (SIZE - new_size[0]) // 2
        ey = (SIZE - new_size[1]) // 2 + 8  # nudge down to optically centre
        logo.alpha_composite(shadow, (ex, ey + 8))
        logo.alpha_composite(emoji_scaled, (ex, ey))

        logo.save(ICONS_DIR / f"{slug}.png", "PNG")
        ok += 1
    return ok


def _png_via_rsvg(rsvg: str, rows) -> int:
    ok = 0
    for slug, _pkg, _cat, _desc in rows:
        svg_path = LOGOS_DIR / f"{slug}.svg"
        png_path = ICONS_DIR / f"{slug}.png"
        try:
            subprocess.run(
                [rsvg, "-w", "512", "-h", "512", "-o", str(png_path), str(svg_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            ok += 1
        except subprocess.CalledProcessError as exc:
            print(f"  rsvg-convert failed for {slug}: {exc.stderr.decode(errors='ignore').strip()}")
    return ok


def _png_via_cairosvg(rows) -> int:
    import cairosvg  # type: ignore
    ok = 0
    for slug, _pkg, _cat, _desc in rows:
        svg_path = LOGOS_DIR / f"{slug}.svg"
        png_path = ICONS_DIR / f"{slug}.png"
        try:
            cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                             output_width=512, output_height=512)
            ok += 1
        except Exception as exc:
            print(f"  cairosvg failed for {slug}: {exc}")
    return ok


def _png_via_magick(magick: str, rows) -> int:
    ok = 0
    for slug, _pkg, _cat, _desc in rows:
        svg_path = LOGOS_DIR / f"{slug}.svg"
        png_path = ICONS_DIR / f"{slug}.png"
        try:
            subprocess.run(
                [magick, "-background", "none", "-resize", "512x512",
                 str(svg_path), str(png_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            ok += 1
        except subprocess.CalledProcessError as exc:
            print(f"  magick failed for {slug}: {exc.stderr.decode(errors='ignore').strip()}")
    return ok


if __name__ == "__main__":
    sys.exit(main())
