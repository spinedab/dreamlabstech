#!/usr/bin/env python3
"""
DreamLabsTech Logo Generator - Phosphor Icon edition

Produces one 512x512 SVG per app in the inventory using Phosphor Icons
(Regular weight, 256x256 viewbox) rendered white on a category gradient.

Unlike the previous emoji-based version, these SVGs contain real <path>
elements so they render reliably in every browser.

Logos are written to assets/logos/{slug}.svg.
Optional PNG versions are written to assets/icons/{slug}.png using
cairosvg (if available). PNG generation is best-effort.
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
# Phosphor Icons v2 - Regular weight - Viewbox 256x256
# ---------------------------------------------------------------------------
ICON_PATHS = {
    "brain": "M248,128a56,56,0,0,0-26.81-47.85,55.69,55.69,0,0,0-9.73-48.46A56,56,0,0,0,128,16a56,56,0,0,0-83.46,15.69,55.69,55.69,0,0,0-9.73,48.46,56,56,0,0,0,0,95.7,55.69,55.69,0,0,0,9.73,48.46A56,56,0,0,0,128,240a56,56,0,0,0,83.46-15.69,55.69,55.69,0,0,0,9.73-48.46A56,56,0,0,0,248,128Z",
    "heart": "M178,40c-20.65,0-38.73,8.88-50,23.89C116.73,48.88,98.65,40,78,40a62.07,62.07,0,0,0-62,62c0,78,103.79,135.48,108.21,137.89a8,8,0,0,0,7.58,0C136.21,237.48,240,180,240,102A62.07,62.07,0,0,0,178,40Z",
    "barbell": "M248,120H240V88a8,8,0,0,0-8-8H208a8,8,0,0,0-8,8v16H56V88a8,8,0,0,0-8-8H24a8,8,0,0,0-8,8v32H8a8,8,0,0,0,0,16h8v32a8,8,0,0,0,8,8H48a8,8,0,0,0,8-8V152H200v16a8,8,0,0,0,8,8h24a8,8,0,0,0,8-8V136h8a8,8,0,0,0,0-16Z",
    "chef-hat": "M208,80a39.89,39.89,0,0,0-13.38,2.29,48,48,0,0,0-93.24,0A40,40,0,0,0,48,160a8,8,0,0,0,.29,2.18L64.9,222.56A8,8,0,0,0,72.6,228h110.8a8,8,0,0,0,7.7-5.44l16.6-60.38A8,8,0,0,0,208,160a40,40,0,0,0,0-80Z",
    "book": "M208,24H72A32,32,0,0,0,40,56V224a8,8,0,0,0,8,8H192a8,8,0,0,0,0-16H56a16,16,0,0,1,16-16H208a8,8,0,0,0,8-8V32A8,8,0,0,0,208,24Z",
    "code": "M69.12,94.15,28.5,128l40.62,33.85a8,8,0,1,1-10.24,12.29l-48-40a8,8,0,0,1,0-12.29l48-40a8,8,0,1,1,10.24,12.3Zm176,27.7-48-40a8,8,0,1,0-10.24,12.3L227.5,128l-40.62,33.85a8,8,0,1,0,10.24,12.29l48-40a8,8,0,0,0,0-12.29ZM162.73,32.48a8,8,0,0,0-10.25,4.79l-64,176a8,8,0,0,0,4.79,10.26,8.14,8.14,0,0,0,2.73.48,8,8,0,0,0,7.52-5.27l64-176A8,8,0,0,0,162.73,32.48Z",
    "wallet": "M216,64H56a8,8,0,0,1,0-16H192a8,8,0,0,0,0-16H56A24,24,0,0,0,32,56V184a24,24,0,0,0,24,24H216a16,16,0,0,0,16-16V80A16,16,0,0,0,216,64Zm-36,80a12,12,0,1,1,12-12A12,12,0,0,1,180,144Z",
    "check-square": "M229.66,66.34l-56-56A8,8,0,0,0,168,8H88a16,16,0,0,0-16,16V40H56A16,16,0,0,0,40,56V216a16,16,0,0,0,16,16H168a16,16,0,0,0,16-16V200h16a16,16,0,0,0,16-16V72A8,8,0,0,0,229.66,66.34ZM168,216H56V56H88V184a16,16,0,0,0,16,16h64Zm32-32H104V24h64V64a8,8,0,0,0,8,8h24Z",
    "message": "M128,24A104,104,0,0,0,36.18,176.88L24.83,210.93a16,16,0,0,0,20.24,20.24l34.05-11.35A104,104,0,1,0,128,24Z",
    "sparkle": "M197.58,129.06l-51.61-19-19-51.65a15.92,15.92,0,0,0-29.88,0L78.07,110l-51.65,19a15.92,15.92,0,0,0,0,29.88L78,178l19,51.62a15.92,15.92,0,0,0,29.88,0l19-51.61,51.65-19a15.92,15.92,0,0,0,0-29.88ZM144.48,164a8,8,0,0,0-4.73,4.72L120,222.33l-19.75-53.63A8,8,0,0,0,95.53,164L41.9,144.25,95.53,124.5a8,8,0,0,0,4.72-4.73L120,66.14l19.75,53.63a8,8,0,0,0,4.73,4.73l53.63,19.75Z",
    "smiley": "M128,24A104,104,0,1,0,232,128,104.12,104.12,0,0,0,128,24ZM80,108a12,12,0,1,1,12,12A12,12,0,0,1,80,108Zm92.65,43.41a64.18,64.18,0,0,1-89.3,0,8,8,0,0,1,11.3-11.32,48.17,48.17,0,0,0,66.7,0,8,8,0,0,1,11.3,11.32ZM164,120a12,12,0,1,1,12-12A12,12,0,0,1,164,120Z",
    "leaf": "M223.45,40.07a8,8,0,0,0-7.52-7.52C139.8,28.08,78.82,51,52.82,94c-14.5,24-17.46,52.42-8.69,82.89,3.26,11.33,8.31,20.3,14.9,26.74a72.1,72.1,0,0,1,4.93-20.46,71.85,71.85,0,0,1,24.48-30.53A135.9,135.9,0,0,1,124,120.77C78.07,140.17,57.15,182.58,44,229.51a8,8,0,0,0,15.42,4.37C70.49,198,93.5,162.83,144,144.67c40.68-14.61,77.49-44.09,77.49-97.18Q223.53,45.47,223.45,40.07Z",
    "money": "M240,72H224V56a16,16,0,0,0-16-16H48A16,16,0,0,0,32,56V72H16a8,8,0,0,0-8,8V192a16,16,0,0,0,16,16H232a16,16,0,0,0,16-16V80A8,8,0,0,0,240,72ZM208,56V192H48V56Z",
    "chart": "M232,208a8,8,0,0,1-8,8H32a8,8,0,0,1-8-8V48a8,8,0,0,1,16,0V147.31l42.34-42.35a8,8,0,0,1,11.32,0L128,132.69l42.34-42.35a8,8,0,0,1,11.32,11.32l-48,48a8,8,0,0,1-11.32,0L88,117.31,40,165.31V200H224A8,8,0,0,1,232,208Z",
    "shield": "M208,40H48A16,16,0,0,0,32,56v58.78c0,89.61,75.82,119.34,91,124.39a15.53,15.53,0,0,0,10,0c15.2-5.05,91-34.78,91-124.39V56A16,16,0,0,0,208,40Z",
    "cake": "M120,80V48a8,8,0,0,1,16,0V80a8,8,0,0,1-16,0Zm48,8a8,8,0,0,0,8-8V48a8,8,0,0,0-16,0V80A8,8,0,0,0,168,88Zm64,40v88a16,16,0,0,1-16,16H40a16,16,0,0,1-16-16V128a16,16,0,0,1,16-16H56V88a16,16,0,0,1,16-16H184a16,16,0,0,1,16,16v24h16A16,16,0,0,1,232,128ZM88,48a8,8,0,0,0,8-8V8a8,8,0,0,0-16,0V40A8,8,0,0,0,88,48Z",
    "music": "M212.92,25.69a8,8,0,0,0-6.86-1.45l-128,32A8,8,0,0,0,72,64V174.1A36,36,0,1,0,88,204V70.25l112-28v99.85A36,36,0,1,0,216,172V32A8,8,0,0,0,212.92,25.69Z",
    "footprints": "M112,148a32,32,0,1,1,32-32A32,32,0,0,1,112,148Z",
    "flag": "M42.76,50A8,8,0,0,0,40,56V224a8,8,0,0,0,16,0V179.77c26.79-21.16,49.87-9.75,76.45,3.42,16.4,8.11,33.83,16.73,51.88,16.73,13.62,0,27.6-4.92,41.29-18.6A8,8,0,0,0,228,175.59V50.43a8,8,0,0,0-5.89-7.72C186.5,23.5,158.36,37.5,131.28,50.94,104.34,64.29,78.61,76.38,42.76,50Z",
    "house": "M224,115.55V208a16,16,0,0,1-16,16H168a16,16,0,0,1-16-16V168a8,8,0,0,0-8-8H112a8,8,0,0,0-8,8v40a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V115.55a16,16,0,0,1,5.17-11.78l80-75.48.11-.11a16,16,0,0,1,21.53,0,1.14,1.14,0,0,0,.11.11l80,75.48A16,16,0,0,1,224,115.55Z",
    "camera": "M208,56H180.28L166.65,35.56A8,8,0,0,0,160,32H96a8,8,0,0,0-6.65,3.56L75.72,56H48A24,24,0,0,0,24,80V192a24,24,0,0,0,24,24H208a24,24,0,0,0,24-24V80A24,24,0,0,0,208,56ZM128,176a36,36,0,1,1,36-36A36,36,0,0,1,128,176Z",
    "globe": "M128,24A104,104,0,1,0,232,128,104.12,104.12,0,0,0,128,24Z",
    "car": "M240,112H229.2L201.42,49.5A16,16,0,0,0,186.8,40H69.2a16,16,0,0,0-14.62,9.5L26.8,112H16a8,8,0,0,0,0,16h8v80a16,16,0,0,0,16,16H64a16,16,0,0,0,16-16V192h96v16a16,16,0,0,0,16,16h24a16,16,0,0,0,16-16V128h8a8,8,0,0,0,0-16ZM69.2,56H186.8l24.89,56H44.31Z",
    "lock": "M208,80H176V56a48,48,0,0,0-96,0V80H48A16,16,0,0,0,32,96V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V96A16,16,0,0,0,208,80ZM96,56a32,32,0,0,1,64,0V80H96Z",
    "paint": "M88,232a8,8,0,0,1-8,8H56a8,8,0,0,1-8-8,64,64,0,0,1,64-64V104a8,8,0,0,1,3.16-6.38l72-54.66a15.77,15.77,0,0,1,21.66,1.29l21.54,21.51a15.82,15.82,0,0,1,1.24,21.59L177,159.63A8,8,0,0,1,170.7,163l-42.78.32A64,64,0,0,1,88,232Z",
    "calendar": "M208,32H184V24a8,8,0,0,0-16,0v8H88V24a8,8,0,0,0-16,0v8H48A16,16,0,0,0,32,48V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V48A16,16,0,0,0,208,32Zm0,176H48V96H208V208Z",
    "shopping": "M230.14,70.54,185.46,25.85A20,20,0,0,0,171.31,20H84.69a20,20,0,0,0-14.15,5.86L25.85,70.54A20,20,0,0,0,20,84.69V168a20,20,0,0,0,20,20H216a20,20,0,0,0,20-20V84.69A20,20,0,0,0,230.14,70.54Z",
    "game": "M224,72H32A16,16,0,0,0,16,88v80a16,16,0,0,0,16,16H224a16,16,0,0,0,16-16V88A16,16,0,0,0,224,72Z",
    "newspaper": "M224,40H32A16,16,0,0,0,16,56V200a24,24,0,0,0,24,24H216a24,24,0,0,0,24-24V56A16,16,0,0,0,224,40Z",
    "star": "M234.29,114.85l-45,38.83L203,211.75a16.4,16.4,0,0,1-24.5,17.82L128,198.49,77.47,229.57A16.4,16.4,0,0,1,53,211.75l13.76-58.07-45-38.83A16.46,16.46,0,0,1,31.08,86l59-4.76,22.76-55.08a16.36,16.36,0,0,1,30.27,0L165.9,81.27l59,4.76a16.46,16.46,0,0,1,9.37,28.82Z",
    "bell": "M221.8,175.94C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H88.81a40,40,0,0,0,78.38,0H208a16,16,0,0,0,13.8-24.06Z",
    "phone": "M222.37,158.46l-47.11-21.11-.13-.06a16,16,0,0,0-15.17,1.4,8.12,8.12,0,0,0-.75.56L134.87,160c-15.42-7.49-31.34-23.29-38.83-38.51l20.78-24.71c.2-.25.39-.5.57-.77a16,16,0,0,0,1.32-15.06l0-.12L97.54,33.64a16,16,0,0,0-16.62-9.52A56.26,56.26,0,0,0,32,80c0,79.4,64.6,144,144,144a56.26,56.26,0,0,0,55.88-48.92A16,16,0,0,0,222.37,158.46Z",
    "gear": "M128,80a48,48,0,1,0,48,48A48.05,48.05,0,0,0,128,80Z",
    "gift": "M216,72H180.92c.39-.33.79-.65,1.17-1a29.53,29.53,0,0,0,0-41.57c-11.5-11.46-31.41-11.45-42.84,0a60.26,60.26,0,0,0-11.25,17,60.26,60.26,0,0,0-11.25-17c-11.43-11.45-31.34-11.46-42.84,0a29.53,29.53,0,0,0,0,41.57c.38.38.78.7,1.17,1H40A16,16,0,0,0,24,88v32a16,16,0,0,0,16,16v64a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V136a16,16,0,0,0,16-16V88A16,16,0,0,0,216,72Z",
    "target": "M128,24A104,104,0,1,0,232,128,104.12,104.12,0,0,0,128,24Zm0,144a40,40,0,1,1,40-40A40,40,0,0,1,128,168Z",
    "lightning": "M215.79,118.17a8,8,0,0,0-5-5.66L153.18,90.9l14.66-73.33a8,8,0,0,0-13.69-7l-112,120a8,8,0,0,0,3,13l57.63,21.61L88.16,238.43a8,8,0,0,0,13.69,7l112-120A8,8,0,0,0,215.79,118.17Z",
}

# ---------------------------------------------------------------------------
# Slug -> category map (copied from generate.py so this script is standalone)
# ---------------------------------------------------------------------------
SLUG_CATEGORY = {
    # Salud Mental
    "zenmind_app": "Salud Mental", "mindcare_app": "Salud Mental",
    "mindshift_app": "Salud Mental", "calmapp_app": "Salud Mental",
    "calmkids_app": "Salud Mental", "boostme_app": "Salud Mental",
    "vrtherapy_app": "Salud Mental", "kidmind_app": "Salud Mental",
    "socialskills_app": "Salud Mental", "tremortest": "Salud Mental",
    "focusblink": "Salud Mental",
    # Fitness
    "yogaflow_app": "Fitness", "yogaflow_levels_app": "Fitness",
    "fitbuddy_app": "Fitness", "runmaster_app": "Fitness",
    "workout_log": "Fitness", "sleeptracker_app": "Fitness",
    "trailexplorer_app": "Fitness",
    # Finanzas
    "finantrack_app": "Finanzas", "couplefinance_app": "Finanzas",
    "kidfinance_app": "Finanzas", "pocket_expenses": "Finanzas",
    "subscription_tracker": "Finanzas", "receipt_splitter": "Finanzas",
    "paylat_neobank": "Finanzas",
    # Alimentacion
    "recipefinder_app": "Alimentacion", "chefin_app": "Alimentacion",
    "cookmaster_app": "Alimentacion", "healthybites_app": "Alimentacion",
    "nutritrack_app": "Alimentacion", "kitchenhelper_app": "Alimentacion",
    "meal_planner": "Alimentacion",
    # Productividad
    "taskmaster_app": "Productividad", "taskboard_pro": "Productividad",
    "myproject_app": "Productividad", "teamproject_app": "Productividad",
    "daily_journal": "Productividad", "notevault": "Productividad",
    "goal_compass": "Productividad", "habit_streaks": "Productividad",
    "event_planner": "Productividad", "eventmaster_app": "Productividad",
    "eventonline_app": "Productividad", "shopping_smartlist": "Productividad",
    "travel_packing_list": "Productividad", "cleaning_checklist": "Productividad",
    "creativehub_app": "Productividad",
    # Educacion
    "codelab_app": "Educacion", "linguaar_app": "Educacion",
    "signlang_app": "Educacion", "learnfun_app": "Educacion",
    "autismlearn_app": "Educacion", "writemaster_app": "Educacion",
    "photoguide_app": "Educacion", "brainboost_app": "Educacion",
    "mylibrary_app": "Educacion", "book_tracker": "Educacion",
    "musicmaster_app": "Educacion", "factcheck_app": "Educacion",
    "negotia_app": "Educacion",
    # Estilo de Vida
    "petcare_app": "Estilo de Vida", "plant_pal": "Estilo de Vida",
    "greenlife_app": "Estilo de Vida", "ecotrack_app": "Estilo de Vida",
    "eco_track": "Estilo de Vida", "seniorcare_app": "Estilo de Vida",
    "meditrack_app": "Estilo de Vida", "medai_app": "Estilo de Vida",
    "medremind_app": "Estilo de Vida", "skinmole_tracker": "Estilo de Vida",
    "wanderguide_app": "Estilo de Vida", "tripplanner_app": "Estilo de Vida",
    "weatherguard_app": "Estilo de Vida",
    # Musica
    "piano_app": "Musica", "aimusiccreator": "Musica",
    "pro_audio_eq": "Musica", "retro_amp": "Musica",
    "dj_pro_mobile": "Musica", "bpm_matcher": "Musica",
    "humtotabs": "Musica",
    # Herramientas
    "solarpath_ar": "Herramientas", "wallscanner": "Herramientas",
    "fake_shutdown": "Herramientas", "anti_eavesdrop": "Herramientas",
    "speakercleaner": "Herramientas", "barometer_altimeter": "Herramientas",
    "localdrop": "Herramientas", "frequency_counter": "Herramientas",
    "dashboard_ar": "Herramientas", "threadcount": "Herramientas",
    "level_laser_ar": "Herramientas", "screen_obscure": "Herramientas",
    "applocker_dynamic": "Herramientas", "coin_counter_ai": "Herramientas",
    "arhome_app": "Herramientas", "protomaker_app": "Herramientas",
    "carfix_app": "Herramientas", "car_care_log": "Herramientas",
    "warranty_tracker": "Herramientas", "matter_app": "Herramientas",
    "sign_translator_ar": "Herramientas", "smsblast": "Herramientas",
    # Social
    "networkpro_app": "Social", "periodico_app": "Social",
    "popcorn_app": "Social", "myspace_reimagined": "Social",
    "unova_social": "Social", "tiktok_clone": "Social",
    "whatsapp_clone": "Social",
    # Ecommerce
    "hospedajeco": "Ecommerce", "marketco_marketplace": "Ecommerce",
    "latamgo_delivery": "Ecommerce", "mercadonova": "Ecommerce",
    "portapro_app": "Ecommerce",
    # Juegos
    "alfa_computacional": "Juegos", "dados_flutter": "Juegos",
    "gravity_dodger": "Juegos",
    # Negocios
    "client_crm_lite": "Negocios", "service_ticket_desk": "Negocios",
    "inventory_manager": "Negocios", "hotelmaster_app": "Negocios",
    "demo": "Negocios", "rider_app": "Negocios", "driver_app": "Negocios",
    "superapp": "Negocios", "rider": "Negocios", "driver": "Negocios",
}

# ---------------------------------------------------------------------------
# Slug -> Phosphor icon map (one per app, themed to purpose)
# ---------------------------------------------------------------------------
APP_ICON_MAP = {
    # Salud Mental
    "zenmind_app":        "leaf",
    "mindcare_app":       "brain",
    "mindshift_app":      "brain",
    "calmapp_app":        "leaf",
    "calmkids_app":       "smiley",
    "boostme_app":        "lightning",
    "vrtherapy_app":      "sparkle",
    "kidmind_app":        "smiley",
    "socialskills_app":   "message",
    "tremortest":         "heart",
    "focusblink":         "target",

    # Fitness
    "yogaflow_app":        "leaf",
    "yogaflow_levels_app": "chart",
    "fitbuddy_app":        "barbell",
    "runmaster_app":       "footprints",
    "workout_log":         "barbell",
    "sleeptracker_app":    "bell",
    "trailexplorer_app":   "footprints",

    # Finanzas
    "finantrack_app":       "chart",
    "couplefinance_app":    "heart",
    "kidfinance_app":       "money",
    "pocket_expenses":      "wallet",
    "subscription_tracker": "calendar",
    "receipt_splitter":     "money",
    "paylat_neobank":       "wallet",

    # Alimentacion
    "recipefinder_app":  "chef-hat",
    "chefin_app":        "chef-hat",
    "cookmaster_app":    "chef-hat",
    "healthybites_app":  "leaf",
    "nutritrack_app":    "leaf",
    "kitchenhelper_app": "chef-hat",
    "meal_planner":      "cake",

    # Productividad
    "taskmaster_app":      "check-square",
    "taskboard_pro":       "check-square",
    "myproject_app":       "target",
    "teamproject_app":     "check-square",
    "daily_journal":       "book",
    "notevault":           "book",
    "goal_compass":        "target",
    "habit_streaks":       "lightning",
    "event_planner":       "calendar",
    "eventmaster_app":     "calendar",
    "eventonline_app":     "camera",
    "shopping_smartlist":  "shopping",
    "travel_packing_list": "flag",
    "cleaning_checklist":  "check-square",
    "creativehub_app":     "paint",

    # Educacion
    "codelab_app":     "code",
    "linguaar_app":    "globe",
    "signlang_app":    "message",
    "learnfun_app":    "book",
    "autismlearn_app": "sparkle",
    "writemaster_app": "book",
    "photoguide_app":  "camera",
    "brainboost_app":  "brain",
    "mylibrary_app":   "book",
    "book_tracker":    "book",
    "musicmaster_app": "music",
    "factcheck_app":   "check-square",
    "negotia_app":     "message",

    # Estilo de Vida
    "petcare_app":       "heart",
    "plant_pal":         "leaf",
    "greenlife_app":     "leaf",
    "ecotrack_app":      "globe",
    "eco_track":         "leaf",
    "seniorcare_app":    "heart",
    "meditrack_app":     "heart",
    "medai_app":         "brain",
    "medremind_app":     "bell",
    "skinmole_tracker":  "target",
    "wanderguide_app":   "globe",
    "tripplanner_app":   "flag",
    "weatherguard_app":  "shield",

    # Musica
    "piano_app":       "music",
    "aimusiccreator":  "sparkle",
    "pro_audio_eq":    "music",
    "retro_amp":       "music",
    "dj_pro_mobile":   "music",
    "bpm_matcher":     "music",
    "humtotabs":       "music",

    # Herramientas
    "solarpath_ar":        "lightning",
    "wallscanner":         "target",
    "fake_shutdown":       "lock",
    "anti_eavesdrop":      "shield",
    "speakercleaner":      "bell",
    "barometer_altimeter": "chart",
    "localdrop":           "lightning",
    "frequency_counter":   "chart",
    "dashboard_ar":        "car",
    "threadcount":         "target",
    "level_laser_ar":      "target",
    "screen_obscure":      "shield",
    "applocker_dynamic":   "lock",
    "coin_counter_ai":     "money",
    "arhome_app":          "house",
    "protomaker_app":      "gear",
    "carfix_app":          "gear",
    "car_care_log":        "car",
    "warranty_tracker":    "shield",
    "matter_app":          "house",
    "sign_translator_ar":  "message",
    "smsblast":            "message",

    # Social
    "networkpro_app":     "message",
    "periodico_app":      "newspaper",
    "popcorn_app":        "star",
    "myspace_reimagined": "star",
    "unova_social":       "globe",
    "tiktok_clone":       "camera",
    "whatsapp_clone":     "message",

    # Ecommerce
    "hospedajeco":          "house",
    "marketco_marketplace": "shopping",
    "latamgo_delivery":     "car",
    "mercadonova":          "shopping",
    "portapro_app":         "star",

    # Juegos
    "alfa_computacional": "game",
    "dados_flutter":      "game",
    "gravity_dodger":     "star",

    # Negocios
    "client_crm_lite":     "check-square",
    "service_ticket_desk": "check-square",
    "inventory_manager":   "shopping",
    "hotelmaster_app":     "house",
    "demo":                "gear",
    "rider_app":           "car",
    "driver_app":          "car",
    "superapp":            "phone",
    "rider":               "flag",
    "driver":              "car",
}


# ---------------------------------------------------------------------------
# SVG builder
# ---------------------------------------------------------------------------
def build_svg(slug: str, c1: str, c2: str, icon_path: str) -> str:
    """Build a 512x512 SVG logo containing a real white icon path."""
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", slug)
    # Phosphor icons are 256x256. We want them at ~60% of the 512 tile (~307 px),
    # so we scale by 1.2 and translate to keep them centred.
    # Scaled size = 256 * 1.2 = 307.2; offset = (512 - 307.2) / 2 ~ 102.4
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 512 512\" role=\"img\" aria-label=\"{slug} logo\">
  <defs>
    <linearGradient id=\"bg_{safe_id}\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">
      <stop offset=\"0%\" stop-color=\"{c1}\"/>
      <stop offset=\"100%\" stop-color=\"{c2}\"/>
    </linearGradient>
    <radialGradient id=\"glow_{safe_id}\" cx=\"50%\" cy=\"52%\" r=\"42%\">
      <stop offset=\"0%\" stop-color=\"#ffffff\" stop-opacity=\"0.35\"/>
      <stop offset=\"60%\" stop-color=\"#ffffff\" stop-opacity=\"0.08\"/>
      <stop offset=\"100%\" stop-color=\"#ffffff\" stop-opacity=\"0\"/>
    </radialGradient>
    <filter id=\"shadow_{safe_id}\" x=\"-10%\" y=\"-10%\" width=\"120%\" height=\"120%\">
      <feDropShadow dx=\"0\" dy=\"4\" stdDeviation=\"6\" flood-color=\"#000000\" flood-opacity=\"0.22\"/>
    </filter>
  </defs>
  <rect x=\"0\" y=\"0\" width=\"512\" height=\"512\" rx=\"96\" ry=\"96\" fill=\"url(#bg_{safe_id})\"/>
  <circle cx=\"256\" cy=\"266\" r=\"180\" fill=\"url(#glow_{safe_id})\"/>
  <g transform=\"translate(102.4, 102.4) scale(1.2)\" fill=\"white\" filter=\"url(#shadow_{safe_id})\">
    <path d=\"{icon_path}\"/>
  </g>
</svg>
"""


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------
def read_inventory(path: str):
    """Try to read /tmp/apps_inventory.txt; fall back to SLUG_CATEGORY map."""
    rows = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                while len(parts) < 4:
                    parts.append("")
                slug, pkg, category, desc = parts[0], parts[1], parts[2], "|".join(parts[3:])
                rows.append((slug, pkg, category, desc))
    if rows:
        return rows
    # Fallback: build from embedded SLUG_CATEGORY
    for slug, category in SLUG_CATEGORY.items():
        rows.append((slug, f"com.spinedab.{slug}", category, ""))
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    rows = read_inventory(INVENTORY)
    total = len(rows)
    print(f"[generate_logos] {total} apps found")

    missing_icon = []
    for slug, _pkg, category, _desc in rows:
        primary, accent = PALETTE.get(category, PALETTE["Herramientas"])
        icon_name = APP_ICON_MAP.get(slug, "sparkle")
        if slug not in APP_ICON_MAP:
            missing_icon.append(slug)
        icon_path = ICON_PATHS.get(icon_name, ICON_PATHS["sparkle"])

        svg = build_svg(slug, primary, accent, icon_path)
        (LOGOS_DIR / f"{slug}.svg").write_text(svg, encoding="utf-8")

    print(f"[generate_logos] Wrote {total} SVGs to {LOGOS_DIR}")
    if missing_icon:
        print(f"[generate_logos] WARNING: fell back to 'sparkle' for {len(missing_icon)}: "
              f"{', '.join(missing_icon[:10])}"
              + (" ..." if len(missing_icon) > 10 else ""))

    png_count = write_pngs(rows)
    print(f"[generate_logos] Wrote {png_count} PNGs to {ICONS_DIR}")
    return 0


def write_pngs(rows) -> int:
    """Render PNGs via cairosvg (best-effort)."""
    try:
        import cairosvg  # noqa: F401
        print("[generate_logos] Using cairosvg for PNGs")
    except Exception as exc:
        print(f"[generate_logos] cairosvg unavailable ({exc}); trying rsvg-convert")
        rsvg = shutil.which("rsvg-convert")
        if rsvg:
            return _png_via_rsvg(rsvg, rows)
        print("[generate_logos] No SVG->PNG converter available; skipping PNGs")
        return 0

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


if __name__ == "__main__":
    sys.exit(main())
