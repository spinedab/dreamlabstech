#!/usr/bin/env python3
"""
DreamLabsTech Landing Page Generator
Generates a master index.html plus one landing page per app
for all apps listed in /tmp/apps_inventory.txt.
"""
import os
import re
import html
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
INVENTORY = "/tmp/apps_inventory.txt"
BASE = Path("/Users/mac_mini2/Documents/GitHub/spinedab/landing-pages")
APPS_DIR = BASE / "apps"
APPS_DIR.mkdir(parents=True, exist_ok=True)

PLAY_STORE_TMPL = "https://play.google.com/store/apps/details?id={pkg}"

# Canonical user-facing categories (order = filter order)
CATEGORIES = [
    "Salud Mental", "Fitness", "Finanzas", "Alimentacion", "Productividad",
    "Educacion", "Estilo de Vida", "Musica", "Herramientas", "Social",
    "Ecommerce", "Juegos", "Negocios",
]

# Category colour palette (primary / accent)
PALETTE = {
    "Salud Mental":    ("#2E7D92", "#A8DADC"),
    "Fitness":         ("#FF5722", "#FF9800"),
    "Finanzas":        ("#1565C0", "#00BFA5"),
    "Alimentacion":    ("#FF8C00", "#4CAF50"),
    "Productividad":   ("#0D47A1", "#448AFF"),
    "Educacion":       ("#6200EA", "#FF6D00"),
    "Estilo de Vida":  ("#2E7D32", "#FFC107"),
    "Musica":          ("#263238", "#00E676"),
    "Herramientas":    ("#455A64", "#29B6F6"),
    "Social":          ("#E91E63", "#FF4081"),
    "Ecommerce":       ("#00ACC1", "#FFAB00"),
    "Juegos":          ("#7B1FA2", "#FFEB3B"),
    "Negocios":        ("#37474F", "#FFC400"),
}

# ---------------------------------------------------------------------------
# Classification: map inventory rows to a user-facing category
# ---------------------------------------------------------------------------
# Explicit overrides keyed by app slug (primary name in inventory).
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
    "sign_translator_ar": "Herramientas",

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
# Display metadata (Spanish marketing names + taglines)
# Falls back to a generated display name if slug not listed.
# ---------------------------------------------------------------------------
DISPLAY = {
    "solarpath_ar":      ("SolarPath AR",           "Planifica instalaciones solares con realidad aumentada"),
    "wallscanner":       ("WallScanner",            "Detecta cables y tuberias ocultos en paredes"),
    "fake_shutdown":     ("Fake Shutdown",          "Simula el apagado de tu dispositivo al instante"),
    "anti_eavesdrop":    ("Anti Eavesdrop",         "Protege tus conversaciones de escuchas no deseadas"),
    "speakercleaner":    ("Speaker Cleaner",        "Limpia los altavoces eliminando polvo y humedad"),
    "barometer_altimeter":("Barometro y Altimetro", "Lecturas precisas de presion y altitud en tu bolsillo"),
    "localdrop":         ("LocalDrop",              "Comparte archivos al instante en tu red local"),
    "skinmole_tracker":  ("SkinMole Tracker",       "Monitorea lunares y cambios en tu piel"),
    "frequency_counter": ("Frequency Counter",      "Analizador de frecuencias en tiempo real"),
    "dashboard_ar":      ("Dashboard AR",           "Panel de conduccion aumentada para tu auto"),
    "receipt_splitter":  ("Receipt Splitter",       "Divide cuentas y propinas entre amigos sin calculos"),
    "threadcount":       ("Thread Count",           "Mide la densidad de hilos en tejidos con precision"),
    "level_laser_ar":    ("Level Laser AR",         "Nivel laser virtual con realidad aumentada"),
    "tremortest":        ("Tremor Test",            "Evalua temblores finos y registra evolucion"),
    "screen_obscure":    ("Screen Obscure",         "Privacidad visual sobre tu pantalla en segundos"),
    "applocker_dynamic": ("AppLocker Dynamic",      "Bloqueo adaptativo de apps con reglas inteligentes"),
    "bpm_matcher":       ("BPM Matcher",            "Encuentra el tempo perfecto para tus mezclas"),
    "coin_counter_ai":   ("Coin Counter AI",        "Cuenta monedas automaticamente con IA"),
    "humtotabs":         ("Hum to Tabs",            "Tararea una melodia y obten tablaturas al instante"),
    "focusblink":        ("FocusBlink",             "Rompe la fatiga visual con pausas inteligentes"),
    "arhome_app":        ("AR Home",                "Visualiza muebles y decoracion en tu hogar con AR"),
    "protomaker_app":    ("ProtoMaker",             "Prototipa ideas con herramientas visuales rapidas"),
    "medai_app":         ("MedAI",                  "Asistente medico personal con IA"),
    "yogaflow_levels_app":("YogaFlow Levels",       "Yoga progresivo desde principiante hasta avanzado"),
    "recipefinder_app":  ("RecipeFinder",           "Descubre recetas con lo que tienes en la nevera"),
    "sleeptracker_app":  ("SleepTracker",           "Analiza tu sueno y mejora tu descanso"),
    "musicmaster_app":   ("MusicMaster",            "Clases de musica con partituras interactivas"),
    "zenmind_app":       ("ZenMind",                "Mindfulness y respiracion para tu dia a dia"),
    "kitchenhelper_app": ("KitchenHelper",          "Cocina paso a paso con tecnicas profesionales"),
    "chefin_app":        ("Chefin",                 "Aprende a cocinar desde cero con videos guiados"),
    "vrtherapy_app":     ("VR Therapy",             "Terapia asistida por realidad virtual"),
    "carfix_app":        ("CarFix",                 "Diagnostica fallas de tu auto y encuentra ayuda"),
    "kidmind_app":       ("KidMind",                "Guia emocional para padres y ninos"),
    "trailexplorer_app": ("TrailExplorer",          "Descubre rutas de senderismo con mapas y alertas"),
    "networkpro_app":    ("NetworkPro",             "Networking profesional con oportunidades reales"),
    "cookmaster_app":    ("CookMaster",             "Recetas personalizadas con tu despensa"),
    "factcheck_app":     ("FactCheck",              "Verifica fuentes y detecta desinformacion"),
    "eventonline_app":   ("EventOnline",            "Webinars y reuniones virtuales con engagement en vivo"),
    "healthybites_app":  ("HealthyBites",           "Recetas y plan nutricional adaptado a ti"),
    "petcare_app":       ("PetCare",                "Lleva la salud y rutina de tu mascota al dia"),
    "linguaar_app":      ("LinguaAR",               "Aprende idiomas con realidad aumentada inmersiva"),
    "couplefinance_app": ("CoupleFinance",          "Gastos y metas compartidos para parejas"),
    "learnfun_app":      ("LearnFun",               "Aprendizaje adaptativo y divertido para ninos"),
    "finantrack_app":    ("FinanTrack",             "Control financiero personal con insights claros"),
    "tripplanner_app":   ("TripPlanner",            "Crea itinerarios y controla tu presupuesto de viaje"),
    "meditrack_app":     ("MediTrack",              "Agenda medica y salud bajo control"),
    "brainboost_app":    ("BrainBoost",             "Juegos de logica para entrenar tu mente"),
    "mindcare_app":      ("MindCare",               "Bienestar mental con check-ins guiados"),
    "nutritrack_app":    ("NutriTrack",             "Plan diario con macros y metas personalizadas"),
    "socialskills_app":  ("SocialSkills",           "Fortalece tu confianza social con roleplay"),
    "fitbuddy_app":      ("FitBuddy",               "Entrenamientos adaptativos con sync de wearables"),
    "hotelmaster_app":   ("HotelMaster",            "Gestion integral para pequenas hostelerias"),
    "mindshift_app":     ("MindShift",              "Terapia cognitiva para ansiedad y estres"),
    "weatherguard_app":  ("WeatherGuard",           "Clima y alertas de emergencia confiables"),
    "seniorcare_app":    ("SeniorCare",             "Acompanamiento diario y seguridad para mayores"),
    "eventmaster_app":   ("EventMaster",            "Organizador total de eventos y proveedores"),
    "negotia_app":       ("Negotia",                "Entrenador de negociacion con casos reales"),
    "runmaster_app":     ("RunMaster",              "Plan de running con ritmo y progreso inteligente"),
    "ecotrack_app":      ("EcoTrack",               "Mide y reduce tu huella con tips diarios"),
    "calmkids_app":      ("CalmKids",               "Meditacion y sonidos calmantes para ninos"),
    "creativehub_app":   ("CreativeHub",            "Herramientas creativas y galeria colaborativa"),
    "mylibrary_app":     ("MyLibrary",              "Cataloga tus libros y descubre tu proxima lectura"),
    "calmapp_app":       ("CalmApp",                "Relajacion y tecnicas CBT en tu bolsillo"),
    "taskmaster_app":    ("TaskMaster",             "Cabina de productividad con enfoque y metas"),
    "signlang_app":      ("SignLang",               "Aprende lengua de senas con lecciones interactivas"),
    "wanderguide_app":   ("WanderGuide",            "Mapas y recomendaciones locales para tus viajes"),
    "autismlearn_app":   ("AutismLearn",            "Juegos adaptados para ninos en el espectro autista"),
    "medremind_app":     ("MedRemind",              "Recordatorios y reportes de medicacion"),
    "codelab_app":       ("CodeLab",                "Aprende a programar con proyectos reales"),
    "kidfinance_app":    ("KidFinance",             "Educacion financiera divertida para ninos"),
    "greenlife_app":     ("GreenLife",              "Vida sostenible con habitos medibles"),
    "writemaster_app":   ("WriteMaster",            "Mejora tu escritura con feedback inteligente"),
    "photoguide_app":    ("PhotoGuide",             "Lecciones y retos para dominar la fotografia"),
    "boostme_app":       ("BoostMe",                "Autoestima diaria con ejercicios guiados"),
    "yogaflow_app":      ("YogaFlow",               "Yoga guiado con seguimiento de posturas"),
    "myproject_app":     ("MyProject",              "Planifica tus proyectos personales con hitos"),
    "portapro_app":      ("PortaPro",               "Portafolio profesional con branding propio"),
    "teamproject_app":   ("TeamProject",            "Gestion de proyectos de equipo de extremo a extremo"),
    "goal_compass":      ("Goal Compass",           "Metas con fecha y progreso real, todo offline"),
    "daily_journal":     ("Daily Journal",          "Diario personal con estados de animo y notas"),
    "car_care_log":      ("Car Care Log",           "Historial de mantenimientos de tu vehiculo"),
    "warranty_tracker":  ("Warranty Tracker",       "Seguimiento de garantias y vencimientos"),
    "shopping_smartlist":("Shopping SmartList",     "Lista de compras inteligente por categorias"),
    "taskboard_pro":     ("TaskBoard Pro",          "Tablero de tareas con prioridades y estados"),
    "subscription_tracker":("Subscription Tracker", "Controla tus suscripciones y renovaciones"),
    "pocket_expenses":   ("Pocket Expenses",        "Gastos personales organizados en segundos"),
    "notevault":         ("NoteVault",              "Notas con busqueda, etiquetas y pines"),
    "event_planner":     ("Event Planner",          "Agenda eventos con fecha, hora y ubicacion"),
    "travel_packing_list":("Travel Packing List",   "Lista de equipaje inteligente por categorias"),
    "meal_planner":      ("Meal Planner",           "Planifica comidas y recetas sin complicaciones"),
    "client_crm_lite":   ("Client CRM Lite",        "Mini CRM ligero para clientes y seguimientos"),
    "service_ticket_desk":("Service Ticket Desk",   "Gestor simple de tickets de soporte"),
    "book_tracker":      ("Book Tracker",           "Seguimiento de lectura con progreso real"),
    "workout_log":       ("Workout Log",            "Registro de entrenamientos con duracion e intensidad"),
    "inventory_manager": ("Inventory Manager",      "Inventario offline con minimos y ubicaciones"),
    "eco_track":         ("Eco Track",              "Lleva tu huella ecologica bajo control"),
    "cleaning_checklist":("Cleaning Checklist",     "Checklist de limpieza con frecuencias claras"),
    "habit_streaks":     ("Habit Streaks",          "Hábitos con rachas que motivan cada dia"),
    "plant_pal":         ("Plant Pal",              "Cuida tus plantas con recordatorios simples"),
    "demo":              ("InDriver Demo",          "Demo completa del ecosistema rider-driver"),
    "rider_app":         ("InDriver Rider",         "Pide viajes con tarifas negociables"),
    "driver_app":        ("InDriver Driver",        "Acepta viajes y gestiona tu jornada"),
    "periodico_app":     ("Periodico Pro",          "Titulares RSS y fuentes curadas en un solo feed"),
    "popcorn_app":       ("Popcorn",                "Streaming con descargas offline y reproduccion VLC"),
    "alfa_computacional":("Alfa Computacional",     "Analitica deportiva con Dixon-Coles y Kelly"),
    "dados_flutter":     ("Dados Flutter",          "Lanza dados y compila tu APK localmente"),
    "matter_app":        ("Matter",                 "Inventario visual del mundo fisico"),
    "hospedajeco":       ("Hospedaje.co",           "Metabuscador de hoteles para Colombia"),
    "paylat_neobank":    ("PayLat",                 "Neobanco digital para Latinoamerica"),
    "marketco_marketplace":("MarketCO",             "Marketplace P2P para Colombia"),
    "latamgo_delivery":  ("LatamGo",                "Delivery todo-en-uno para Latinoamerica"),
    "mercadonova":       ("MercadoNova",            "Plataforma e-commerce pensada para LatAm"),
    "gravity_dodger":    ("Gravity Dodger",         "Arcade de reflejos con fisica invertida"),
    "rider":             ("AntiGravity Rider",      "Pasajeros de nueva generacion con IA"),
    "superapp":          ("AntiGravity SuperApp",   "Rider y driver unificados con modo demo"),
    "driver":            ("AntiGravity Driver",     "Conductores potenciados con IA y ML"),
    "sign_translator_ar":("Sign Translator AR",     "Traduce senas en tiempo real con AR"),
    "myspace_reimagined":("MySpace Reimagined",     "Red social con glassmorphism y animaciones fluidas"),
    "unova_social":      ("Unova Social",           "Red social centrada en comunidades activas"),
    "tiktok_clone":      ("ShortVideos",            "Plataforma de videos cortos con feed infinito"),
    "whatsapp_clone":    ("SecureChat",             "Mensajeria con cifrado E2EE profesional"),
    "piano_app":         ("Virtual Piano",          "Piano tactil con multi-octava y audio real"),
    "aimusiccreator":    ("AI Music Creator",       "Genera musica local sin APIs externas"),
    "pro_audio_eq":      ("Pro Audio EQ",           "Ecualizador y mastering con 10 bandas"),
    "retro_amp":         ("Retro AMP",              "Reproductor retro con skins y visualizador"),
    "dj_pro_mobile":     ("ProMix DJ Studio",       "DJ studio con dual-deck y efectos"),
}

# ---------------------------------------------------------------------------
# Category copy bank (features, benefits, FAQs)
# ---------------------------------------------------------------------------
CAT_FEATURES = {
    "Salud Mental": [
        ("Sesiones guiadas", "Meditaciones y ejercicios narrados disenados por profesionales en bienestar."),
        ("Check-in emocional", "Registra tu estado de animo y descubre patrones a lo largo del tiempo."),
        ("Respiracion consciente", "Tecnicas de respiracion con visualizaciones suaves y tiempo ajustable."),
        ("Modo nocturno calmante", "Paletas de color calidas y sonidos que ayudan a desconectar."),
        ("Privacidad total", "Tus datos emocionales permanecen en tu dispositivo, siempre cifrados."),
        ("Progreso motivador", "Estadisticas respetuosas que celebran tu constancia sin juzgar."),
    ],
    "Fitness": [
        ("Planes personalizados", "Rutinas adaptadas a tu nivel, objetivo y equipamiento disponible."),
        ("Seguimiento inteligente", "Metricas de rendimiento claras: volumen, ritmo, calorias y recuperacion."),
        ("Ejercicios guiados", "Animaciones y videos con foco en tecnica para evitar lesiones."),
        ("Sincronizacion wearable", "Integra tus pulseras y relojes para datos en tiempo real."),
        ("Retos y rachas", "Mantente motivado con retos semanales y rachas que celebran la constancia."),
        ("Informes semanales", "Resumen visual de tu progreso y sugerencias para mejorar."),
    ],
    "Finanzas": [
        ("Presupuestos inteligentes", "Define limites mensuales y recibe alertas antes de pasarte."),
        ("Categorizacion automatica", "Clasifica tus gastos por tipo y detecta areas de ahorro."),
        ("Metas de ahorro", "Objetivos con barra de progreso y recordatorios positivos."),
        ("Reportes claros", "Graficos mensuales y anuales sin jerga financiera."),
        ("Multiples cuentas", "Gestiona efectivo, tarjetas y cuentas en un solo panel."),
        ("Datos seguros", "Cifrado local y respaldos manuales sin compartir con terceros."),
    ],
    "Alimentacion": [
        ("Recetas adaptadas", "Sugerencias basadas en tus preferencias, alergias y tiempo disponible."),
        ("Planificador semanal", "Organiza tus comidas y genera la lista de compra automaticamente."),
        ("Macros y nutrientes", "Valores nutricionales claros por receta y por plan diario."),
        ("Modo paso a paso", "Cocina guiada con temporizadores integrados y consejos del chef."),
        ("Reduccion de desperdicio", "Cocina con lo que ya tienes y evita tirar ingredientes."),
        ("Favoritos y colecciones", "Guarda, organiza y comparte tus recetas preferidas."),
    ],
    "Productividad": [
        ("Tareas con prioridades", "Organiza con urgencia, importancia y fechas limite reales."),
        ("Bloques de enfoque", "Sesiones tipo Pomodoro configurables con estadisticas."),
        ("Metas con hitos", "Divide objetivos grandes en pasos accionables."),
        ("Recordatorios contextuales", "Notificaciones inteligentes que no interrumpen tu flujo."),
        ("Modo offline", "Sigue produciendo sin conexion y sincroniza cuando quieras."),
        ("Vistas flexibles", "Lista, tablero o calendario segun como pienses mejor."),
    ],
    "Educacion": [
        ("Lecciones interactivas", "Contenido corto y activo disenado para recordar mejor."),
        ("Evaluaciones inteligentes", "Quizzes que se adaptan a tu nivel en tiempo real."),
        ("Progreso visible", "Ruta de aprendizaje clara con mapa de conocimientos."),
        ("Contenido offline", "Descarga lecciones y practica sin conexion."),
        ("Feedback inmediato", "Explicaciones detalladas en cada respuesta."),
        ("Retos y logros", "Sistema de medallas y retos que celebra cada paso."),
    ],
    "Estilo de Vida": [
        ("Rutinas personalizables", "Crea tus propios habitos con horarios y recordatorios."),
        ("Guias practicas", "Consejos accionables basados en expertos y evidencia."),
        ("Seguimiento suave", "Metricas amables que motivan sin presionar."),
        ("Comunidad opcional", "Comparte avances solo cuando tu quieras."),
        ("Modo offline", "Funciona cuando y donde lo necesites, sin conexion."),
        ("Diseno minimalista", "Interfaz limpia que reduce la fricccion del dia a dia."),
    ],
    "Musica": [
        ("Audio profesional", "Motor de audio de baja latencia optimizado para moviles."),
        ("Controles tactiles", "Interfaz pensada para el gesto, con precision quirurgica."),
        ("Presets curados", "Configuraciones listas para empezar y personalizables al 100%."),
        ("Exportacion simple", "Guarda y comparte tus creaciones en formatos estandar."),
        ("Modo sin conexion", "Todo el flujo musical funciona sin depender de la nube."),
        ("Ajuste fino", "Controles avanzados para productores exigentes."),
    ],
    "Herramientas": [
        ("Medicion precisa", "Resultados confiables usando los sensores de tu dispositivo."),
        ("Interfaz minimalista", "Foco en la tarea, sin distracciones innecesarias."),
        ("Modo oscuro nativo", "Visualizacion comoda en cualquier condicion de luz."),
        ("Sin anuncios intrusivos", "Experiencia limpia y respetuosa con tu tiempo."),
        ("Resultados exportables", "Guarda o comparte tus mediciones en segundos."),
        ("Funciona offline", "Todo el trabajo sucede en tu dispositivo."),
    ],
    "Social": [
        ("Feeds personalizados", "Descubre contenido relevante sin algoritmos invasivos."),
        ("Mensajes seguros", "Conversaciones privadas con cifrado moderno."),
        ("Perfil completo", "Personaliza tu identidad digital sin limites."),
        ("Notificaciones inteligentes", "Solo lo importante llega a tu pantalla."),
        ("Moderacion respetuosa", "Herramientas claras para una comunidad sana."),
        ("Multiplataforma", "Continua tu conversacion entre dispositivos."),
    ],
    "Ecommerce": [
        ("Catalogo inteligente", "Productos organizados para encontrarlos al primer vistazo."),
        ("Pagos seguros", "Pasarelas confiables con multiples metodos."),
        ("Envios en vivo", "Seguimiento de pedidos de principio a fin."),
        ("Favoritos y listas", "Guarda y organiza lo que te interesa."),
        ("Ofertas personalizadas", "Descuentos relevantes, sin spam."),
        ("Soporte cercano", "Chat y ayuda rapida cuando lo necesites."),
    ],
    "Juegos": [
        ("Jugabilidad pulida", "Controles responsivos y fisica afinada al detalle."),
        ("Partidas rapidas", "Diversion inmediata en cualquier momento."),
        ("Progresion satisfactoria", "Niveles y retos que invitan a volver."),
        ("Modo offline", "Juega sin conexion cuando quieras."),
        ("Sin pay-to-win", "Experiencia equilibrada para todos."),
        ("Diseno visual cuidado", "Arte y animaciones que se sienten premium."),
    ],
    "Negocios": [
        ("Panel claro", "Vista unica de lo importante para tu operacion."),
        ("Gestion de contactos", "Clientes, leads y notas siempre organizados."),
        ("Reportes de rendimiento", "Metricas clave en graficos sencillos."),
        ("Multi-dispositivo", "Trabaja desde movil o tablet sin perder contexto."),
        ("Exportacion rapida", "Comparte datos en CSV y PDF cuando lo necesites."),
        ("Modo offline", "Sigue operando sin conexion y sincroniza despues."),
    ],
}

CAT_BENEFITS = {
    "Salud Mental": [
        ("Privacidad de clase clinica", "Tus registros emocionales nunca salen del dispositivo sin tu permiso."),
        ("Diseno calmante", "Cada detalle visual y sonoro esta pensado para bajar la tension."),
        ("Progreso respetuoso", "Te acompanamos sin rachas agresivas ni culpa por pausar."),
    ],
    "Fitness": [
        ("Adaptado a tu ritmo", "Tu plan evoluciona segun tu rendimiento real, no al reves."),
        ("Cero fricccion", "Lanza un entrenamiento en dos toques, sin menus infinitos."),
        ("Resultados medibles", "Metricas relevantes para entender tu evolucion."),
    ],
    "Finanzas": [
        ("Control sin estres", "Vision clara de tu dinero sin hojas de calculo."),
        ("Privacidad primero", "No vendemos ni compartimos tu informacion financiera."),
        ("Sin tarifas ocultas", "Aplicacion transparente, sin micropagos ni suscripciones sorpresa."),
    ],
    "Alimentacion": [
        ("Menos desperdicio", "Aprovecha lo que tienes y come mejor con lo mismo."),
        ("Ahorras tiempo", "Menus y listas listas en segundos."),
        ("Nutricion honesta", "Informacion real, sin promesas milagro."),
    ],
    "Productividad": [
        ("Enfoque real", "Herramientas simples que respetan tu atencion."),
        ("Todo tu sistema", "Tareas, metas y notas conectadas sin friccion."),
        ("Siempre disponible", "Funciona offline y sincroniza cuando quieres."),
    ],
    "Educacion": [
        ("Aprendizaje que dura", "Sesiones cortas con repaso espaciado integrado."),
        ("Contenido de calidad", "Lecciones curadas y verificadas por expertos."),
        ("Motivacion real", "Retos y recompensas que apoyan tu avance."),
    ],
    "Estilo de Vida": [
        ("Pensado para cada dia", "Rutinas realistas para personas reales."),
        ("Diseno que respira", "Interfaz amable y silenciosa."),
        ("Funciona sin conexion", "No depende de la nube para ayudarte."),
    ],
    "Musica": [
        ("Sonido profesional", "Latencia minima y calidad de estudio."),
        ("Control total", "Cada parametro esta a un gesto de distancia."),
        ("Sin pagos en el mundo", "Funcionalidad completa sin compras sorpresa."),
    ],
    "Herramientas": [
        ("Precisa y rapida", "Resultados confiables en el momento exacto."),
        ("Ligera y respetuosa", "No gasta bateria ni datos sin motivo."),
        ("Hecha para durar", "Diseno pulido pensado para uso prolongado."),
    ],
    "Social": [
        ("Tu comunidad, tus reglas", "Herramientas claras para moderar lo que ves."),
        ("Mensajes seguros", "Cifrado moderno para conversaciones privadas."),
        ("Sin algoritmos oscuros", "Feeds transparentes y ajustables."),
    ],
    "Ecommerce": [
        ("Compra con confianza", "Pasarelas seguras y catalogo verificado."),
        ("Experiencia rapida", "Busqueda y checkout en pocos pasos."),
        ("Soporte humano", "Atencion cercana cuando lo necesitas."),
    ],
    "Juegos": [
        ("Diversion inmediata", "Entras y juegas, sin menus interminables."),
        ("Sin anuncios molestos", "Experiencia limpia de principio a fin."),
        ("Retos para volver", "Progresion justa sin atajos de pago."),
    ],
    "Negocios": [
        ("Operacion clara", "Todo lo importante visible al abrir la app."),
        ("Escala contigo", "Funciona para autonomos y equipos pequenos."),
        ("Seguridad empresarial", "Cifrado y respaldos manuales a tu ritmo."),
    ],
}

CAT_FAQ = {
    "Salud Mental": [
        ("Es un sustituto de la terapia profesional?", "No. {app} es una herramienta de bienestar personal. Si necesitas apoyo clinico, consulta con un profesional acreditado."),
        ("Mis datos emocionales son privados?", "Si. Todo queda cifrado en tu dispositivo. No compartimos tus registros con terceros."),
        ("Necesito conexion a internet?", "La mayoria de funciones de {app} funcionan sin conexion. Solo se usa red para sincronizar respaldos si tu lo decides."),
        ("Cuanto tiempo al dia debo usarla?", "Recomendamos entre 5 y 15 minutos. La constancia importa mas que la duracion."),
        ("Puedo exportar mis notas?", "Si. Puedes exportar tus registros a PDF o texto en cualquier momento."),
    ],
    "Fitness": [
        ("Necesito equipo especial?", "No. {app} ofrece rutinas con y sin equipamiento."),
        ("Se adapta a principiantes?", "Si. Los planes se ajustan a tu nivel y evolucionan contigo."),
        ("Puedo sincronizar mi reloj?", "Soportamos pulseras y relojes compatibles con Google Fit y Health Connect."),
        ("Hay planes de pago obligatorios?", "No. {app} ofrece funciones completas sin suscripcion obligatoria."),
        ("Que pasa si no entreno un dia?", "No perderas tu progreso. {app} recalcula tu plan de forma flexible."),
    ],
    "Finanzas": [
        ("{app} accede a mi banco?", "No. {app} funciona con registros manuales o importaciones controladas por ti."),
        ("Mis datos estan seguros?", "Si. Se cifran en tu dispositivo y no se comparten con terceros."),
        ("Funciona sin conexion?", "Si. {app} opera 100% offline, ideal para mantener tus finanzas privadas."),
        ("Puedo exportar mis reportes?", "Exporta a CSV o PDF para tu contabilidad personal."),
        ("Hay version gratuita?", "Si. Las funciones esenciales de {app} son gratuitas."),
    ],
    "Alimentacion": [
        ("Puedo filtrar por alergias?", "Si. {app} soporta filtros por alergias, intolerancias y dietas."),
        ("Las recetas son originales?", "Son recetas curadas y probadas por nuestro equipo culinario."),
        ("Puedo anadir mis propias recetas?", "Si. Puedes crear, editar y guardar recetas personales."),
        ("Incluye valores nutricionales?", "Cada receta muestra calorias y macronutrientes principales."),
        ("Funciona sin internet?", "Si. {app} almacena tus recetas guardadas para acceso offline."),
    ],
    "Productividad": [
        ("Mis datos se sincronizan?", "Opcionalmente. {app} funciona offline y tu decides si usar respaldos."),
        ("Soporta Pomodoro?", "Si. Tienes bloques configurables y metricas de enfoque."),
        ("Puedo usarla en equipo?", "{app} esta enfocada en uso personal, con exportacion para compartir."),
        ("Es gratis?", "Tiene un nucleo gratuito solido y funciones avanzadas opcionales."),
        ("Hay widgets?", "Si. Incluye widgets rapidos para tareas y enfoque."),
    ],
    "Educacion": [
        ("Necesito experiencia previa?", "No. {app} adapta la dificultad a tu nivel inicial."),
        ("Hay certificados?", "Al completar rutas obtienes insignias internas de progreso."),
        ("Funciona offline?", "Si. Puedes descargar lecciones para estudiar sin conexion."),
        ("Esta en espanol?", "Si. {app} esta completamente en espanol."),
        ("Para que edad es recomendable?", "Depende del contenido; cada ruta indica la edad sugerida."),
    ],
    "Estilo de Vida": [
        ("Funciona sin conexion?", "Si. {app} esta pensada para uso cotidiano sin depender de red."),
        ("Mis datos son privados?", "Si. Todo se guarda en tu dispositivo bajo tu control."),
        ("Puedo exportar mis habitos?", "Si. Exporta a CSV o PDF cuando quieras."),
        ("Hay notificaciones?", "Si, totalmente configurables para no agobiarte."),
        ("Tiene modo oscuro?", "Si. Se ajusta automaticamente al sistema."),
    ],
    "Musica": [
        ("Necesito auriculares cableados?", "No. {app} funciona con auriculares alambricos o Bluetooth de baja latencia."),
        ("Puedo exportar mis creaciones?", "Si. Puedes guardar en WAV o MP3 en tu almacenamiento."),
        ("Funciona sin internet?", "Si. Todo el procesamiento sucede en tu dispositivo."),
        ("Es compatible con MIDI?", "Soportamos MIDI en dispositivos Android 8.0 o superior."),
        ("Hay pagos en la app?", "{app} ofrece sus funciones principales sin pagos adicionales."),
    ],
    "Herramientas": [
        ("La medicion es precisa?", "La precision depende de los sensores de tu dispositivo."),
        ("Funciona offline?", "Si. {app} no requiere conexion para operar."),
        ("Consume mucha bateria?", "No. {app} esta optimizada para un consumo minimo."),
        ("Hay anuncios?", "Minimos y no intrusivos."),
        ("Requiere permisos especiales?", "Solo los necesarios para la funcion principal, explicados al inicio."),
    ],
    "Social": [
        ("Mis mensajes estan cifrados?", "Si. {app} aplica cifrado moderno de extremo a extremo."),
        ("Puedo borrar mi cuenta?", "Si, en cualquier momento y sin friccion."),
        ("Hay publicidad?", "{app} limita la publicidad a formatos no intrusivos."),
        ("Puedo moderar mi feed?", "Si. Controlas que ves con filtros y listas claras."),
        ("Funciona en tablet?", "Si. Diseno responsive para tablet y movil."),
    ],
    "Ecommerce": [
        ("Los pagos son seguros?", "Si. Usamos pasarelas verificadas con cifrado bancario."),
        ("Hay seguimiento de envios?", "Si. Puedes ver el estado del pedido en tiempo real."),
        ("Puedo devolver un producto?", "Si, segun la politica del vendedor."),
        ("Hay atencion al cliente?", "Si. Soporte por chat y correo en horario laboral."),
        ("Funciona en mi pais?", "La disponibilidad se ajusta por region; revisa la tienda."),
    ],
    "Juegos": [
        ("Es gratis?", "Si. Puedes jugar sin pagos obligatorios."),
        ("Tiene anuncios?", "Solo pantallas cortas y opcionales para recompensas."),
        ("Funciona offline?", "Si. {app} se disfruta sin conexion."),
        ("Tiene tabla de puntuaciones?", "Si, local y opcionalmente global."),
        ("Es para ninos?", "La edad recomendada se indica en la ficha de Play Store."),
    ],
    "Negocios": [
        ("Funciona offline?", "Si. {app} opera sin conexion y sincroniza cuando quieras."),
        ("Es apto para autonomos?", "Si. Pensada para autonomos y micro equipos."),
        ("Hay exportacion de datos?", "Si. CSV y PDF con un toque."),
        ("Mis datos son privados?", "Si. {app} no comparte tu informacion de negocio."),
        ("Requiere suscripcion?", "El nucleo es gratuito; hay planes opcionales para equipos."),
    ],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", s).strip("-").lower()
    return s or "app"


def pretty_name(slug: str) -> str:
    base = slug.replace("_app", "").replace("_", " ").strip()
    pretty = " ".join(w.capitalize() for w in base.split())
    return pretty or slug or "App"


def classify(slug: str, raw_category: str, desc: str) -> str:
    if slug in SLUG_CATEGORY:
        return SLUG_CATEGORY[slug]
    d = (desc or "").lower()
    s = slug.lower()
    if any(k in s for k in ["mind", "calm", "zen", "therapy", "social_skills"]):
        return "Salud Mental"
    if any(k in s for k in ["fit", "yoga", "run", "workout", "sleep", "trail"]):
        return "Fitness"
    if any(k in s for k in ["finance", "expense", "money", "budget", "coin"]):
        return "Finanzas"
    if any(k in s for k in ["recipe", "cook", "chef", "meal", "nutri", "kitchen"]):
        return "Alimentacion"
    if any(k in s for k in ["task", "journal", "note", "goal", "habit", "plan", "event"]):
        return "Productividad"
    if any(k in s for k in ["learn", "code", "write", "photo", "read", "book", "lang", "sign"]):
        return "Educacion"
    if any(k in s for k in ["pet", "plant", "green", "eco", "senior", "med", "skin", "weather", "travel", "wander", "trip"]):
        return "Estilo de Vida"
    if any(k in s for k in ["music", "piano", "amp", "dj", "audio", "bpm"]):
        return "Musica"
    if any(k in s for k in ["scanner", "level", "ar", "frequency", "threadcount", "locker", "obscure", "localdrop", "barometer", "car"]):
        return "Herramientas"
    if any(k in s for k in ["social", "chat", "tiktok", "whatsapp", "space", "periodico", "popcorn"]):
        return "Social"
    if any(k in s for k in ["market", "delivery", "shop", "mercado", "hospedaje", "paylat", "porta"]):
        return "Ecommerce"
    if any(k in s for k in ["game", "dados", "alfa", "gravity"]):
        return "Juegos"
    # Fallback to Herramientas
    return "Herramientas"


def hex_rgba(hex_color: str, alpha: float = 0.15) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def _looks_english(s: str) -> bool:
    """Heuristic: treat descriptions clearly written in English as english."""
    s = (s or "").lower()
    if not s:
        return False
    # simple heuristic: presence of common english-only words / absence of
    # spanish accents / common spanish connectors
    english_hits = sum(1 for w in (" with ", " and ", " the ", " for ", " your ",
                                   " based ", " across ", " into ", " smart ") if w in f" {s} ")
    spanish_hits = sum(1 for w in (" con ", " para ", " tus ", " tu ", " y ", " de ",
                                   " que ") if w in f" {s} ")
    return english_hits >= 1 and spanish_hits == 0


def normalize_description(desc: str, cat: str, name: str) -> str:
    """Return a 150-250 char Spanish marketing description."""
    d = (desc or "").strip()
    is_placeholder = (not d) or ("flutter project" in d.lower()) or len(d) < 40
    is_english = _looks_english(d)
    base = None if (is_placeholder or is_english) else d
    templates = {
        "Salud Mental":
            "{name} es una herramienta profesional de bienestar mental que integra check-ins emocionales, sesiones guiadas y respiracion consciente para acompanarte dia a dia con respeto y privacidad.",
        "Fitness":
            "{name} convierte tu telefono en un entrenador personal: rutinas adaptativas, metricas claras y sincronizacion con wearables para que cada sesion cuente y el progreso sea visible.",
        "Finanzas":
            "{name} pone tus finanzas personales bajo control con presupuestos inteligentes, metas de ahorro y reportes claros, todo con privacidad real y sin vender tus datos.",
        "Alimentacion":
            "{name} te ayuda a comer mejor con recetas adaptadas, planificador semanal y listas de compra automaticas, reduciendo el desperdicio y ahorrando tiempo en la cocina.",
        "Productividad":
            "{name} organiza tu dia con tareas priorizadas, bloques de enfoque y metas por hitos, funcionando sin conexion y adaptandose a como realmente piensas y trabajas.",
        "Educacion":
            "{name} transforma tu aprendizaje con lecciones cortas interactivas, feedback inmediato y rutas adaptativas que mantienen tu motivacion al maximo cada dia.",
        "Estilo de Vida":
            "{name} suma pequenos habitos que transforman tu rutina: guias claras, recordatorios suaves y seguimiento respetuoso, todo en una experiencia minimalista.",
        "Musica":
            "{name} ofrece una experiencia musical profesional en tu bolsillo, con audio de baja latencia, controles precisos y herramientas pensadas para creadores exigentes.",
        "Herramientas":
            "{name} aprovecha los sensores de tu dispositivo para entregar resultados rapidos y confiables, con interfaz minimalista y cero fricccion en cada medicion.",
        "Social":
            "{name} conecta personas con seguridad: feeds configurables, mensajes cifrados y herramientas claras de moderacion para comunidades mas sanas.",
        "Ecommerce":
            "{name} facilita comprar y vender con catalogos claros, pagos seguros, seguimiento de envios y un soporte cercano que realmente responde.",
        "Juegos":
            "{name} entrega diversion inmediata con jugabilidad pulida, progresion satisfactoria y sin pay-to-win, porque los juegos tienen que sentirse justos.",
        "Negocios":
            "{name} digitaliza tu operacion con panel claro, gestion de contactos y reportes utiles, pensada para autonomos y micro equipos que necesitan agilidad.",
    }
    template = templates.get(cat, templates["Herramientas"])
    text = base if base else template.format(name=name)
    # If base is too short, complement with the template (single sentence).
    if len(text) < 150:
        filler = template.format(name=name)
        # Avoid duplication
        if filler not in text:
            text = (text.rstrip(".") + ". " + filler).strip()
    # Trim on sentence boundary to keep cap <= 240
    if len(text) > 240:
        cutoff = text.rfind(".", 0, 240)
        text = (text[:cutoff + 1] if cutoff > 150 else text[:238].rstrip() + ".")
    return text


# ---------------------------------------------------------------------------
# HTML templates
# ---------------------------------------------------------------------------
APP_ICON_SVG = """<svg viewBox='0 0 64 64' xmlns='http://www.w3.org/2000/svg' aria-hidden='true'>
  <defs>
    <linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>
      <stop offset='0%' stop-color='{primary}'/>
      <stop offset='100%' stop-color='{accent}'/>
    </linearGradient>
  </defs>
  <rect width='64' height='64' rx='14' fill='url(#g)'/>
  <text x='50%' y='55%' text-anchor='middle' font-family='Inter,Arial,sans-serif' font-size='26' font-weight='700' fill='#ffffff'>{letter}</text>
</svg>"""


def build_screens_svg(primary: str, accent: str, label: str) -> str:
    return (
        f"<svg viewBox='0 0 220 440' xmlns='http://www.w3.org/2000/svg' class='w-full h-auto' aria-hidden='true'>"
        f"<rect x='4' y='4' width='212' height='432' rx='28' fill='{primary}' opacity='0.08'/>"
        f"<rect x='14' y='14' width='192' height='412' rx='22' fill='white' stroke='{primary}' stroke-width='2'/>"
        f"<rect x='26' y='38' width='168' height='36' rx='10' fill='{primary}' opacity='0.15'/>"
        f"<rect x='26' y='86' width='168' height='90' rx='12' fill='{accent}' opacity='0.18'/>"
        f"<rect x='26' y='188' width='168' height='14' rx='6' fill='{primary}' opacity='0.22'/>"
        f"<rect x='26' y='210' width='120' height='12' rx='6' fill='{primary}' opacity='0.18'/>"
        f"<rect x='26' y='240' width='78' height='72' rx='12' fill='{accent}' opacity='0.22'/>"
        f"<rect x='116' y='240' width='78' height='72' rx='12' fill='{primary}' opacity='0.18'/>"
        f"<rect x='26' y='326' width='168' height='42' rx='12' fill='{primary}'/>"
        f"<text x='110' y='353' text-anchor='middle' font-family='Inter,Arial,sans-serif' font-size='16' font-weight='700' fill='#fff'>{esc(label)}</text>"
        f"</svg>"
    )


def feature_card(title: str, desc: str, primary: str) -> str:
    return f"""
    <div class=\"feature-card rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700\">
      <div class=\"w-10 h-10 rounded-xl flex items-center justify-center mb-4\" style=\"background:{hex_rgba(primary,0.15)};color:{primary}\">
        <svg xmlns='http://www.w3.org/2000/svg' class='w-5 h-5' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'><path stroke-linecap='round' stroke-linejoin='round' d='M5 13l4 4L19 7'/></svg>
      </div>
      <h3 class=\"font-bold text-lg mb-2 text-slate-900 dark:text-white\">{esc(title)}</h3>
      <p class=\"text-slate-600 dark:text-slate-300 text-sm leading-relaxed\">{esc(desc)}</p>
    </div>"""


def faq_item(q: str, a: str) -> str:
    return f"""
    <details class=\"group rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-4\">
      <summary class=\"cursor-pointer list-none flex items-center justify-between font-semibold text-slate-900 dark:text-white\">
        <span>{esc(q)}</span>
        <svg class='w-5 h-5 text-slate-500 transition-transform group-open:rotate-180' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'><path stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'/></svg>
      </summary>
      <p class=\"mt-3 text-slate-600 dark:text-slate-300 text-sm leading-relaxed\">{esc(a)}</p>
    </details>"""


def app_page(app: dict) -> str:
    name = app["name"]
    slug = app["slug"]
    cat = app["category"]
    primary, accent = app["primary"], app["accent"]
    tagline = app["tagline"]
    desc = app["description"]
    play_url = app["play_url"]
    letter = (name[:1] or "A").upper()

    features = CAT_FEATURES[cat][:6]
    feature_html = "\n".join(feature_card(t, d, primary) for t, d in features)
    benefits = CAT_BENEFITS[cat]
    benefit_html = "\n".join(
        f"""
      <div class=\"rounded-2xl p-6 bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900 border border-slate-200 dark:border-slate-700\">
        <h4 class=\"font-bold text-slate-900 dark:text-white mb-2\" style=\"color:{primary}\">{esc(bt)}</h4>
        <p class=\"text-slate-600 dark:text-slate-300 text-sm leading-relaxed\">{esc(bd)}</p>
      </div>"""
        for bt, bd in benefits
    )
    faqs = CAT_FAQ[cat]
    faq_html = "\n".join(faq_item(q, a.format(app=name)) for q, a in faqs)

    screens = "\n".join(build_screens_svg(primary, accent, lbl) for lbl in (f"{name}", "Caracteristicas", "Perfil"))

    return f"""<!doctype html>
<html lang=\"es\" class=\"scroll-smooth\">
<head>
<meta charset=\"utf-8\"/>
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
<title>{esc(name)} - {esc(tagline)} | DreamLabsTech</title>
<meta name=\"description\" content=\"{esc(desc)}\"/>
<meta property=\"og:title\" content=\"{esc(name)} | DreamLabsTech\"/>
<meta property=\"og:description\" content=\"{esc(desc)}\"/>
<meta property=\"og:type\" content=\"website\"/>
<script src=\"https://cdn.tailwindcss.com\"></script>
<script>
  tailwind.config = {{ darkMode: 'class' }};
  (function () {{
    const saved = localStorage.getItem('dlt-theme');
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'dark' || (!saved && systemDark)) document.documentElement.classList.add('dark');
  }})();
</script>
<style>
  :root {{ --primary: {primary}; --accent: {accent}; }}
  .btn-primary {{ background: var(--primary); color: #fff; }}
  .btn-primary:hover {{ filter: brightness(0.92); }}
  .badge-cat {{ background: {hex_rgba(primary, 0.15)}; color: {primary}; }}
  .hero-glow {{ background: radial-gradient(circle at 50% 0%, {hex_rgba(accent, 0.35)} 0%, transparent 60%); }}
  .dark .hero-glow {{ background: radial-gradient(circle at 50% 0%, {hex_rgba(accent, 0.2)} 0%, transparent 60%); }}
  body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
</style>
</head>
<body class=\"bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100\">

<header class=\"sticky top-0 z-30 backdrop-blur bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800\">
  <div class=\"max-w-6xl mx-auto px-4 h-16 flex items-center justify-between\">
    <a href=\"../index.html\" class=\"flex items-center gap-3\">
      <span class=\"w-9 h-9 rounded-xl flex items-center justify-center text-white font-bold\" style=\"background:linear-gradient(135deg,{primary},{accent})\">{letter}</span>
      <span class=\"font-bold text-slate-900 dark:text-white\">{esc(name)}</span>
    </a>
    <nav class=\"hidden md:flex gap-6 text-sm font-medium\">
      <a href=\"#features\" class=\"hover:opacity-75\">Caracteristicas</a>
      <a href=\"#screens\" class=\"hover:opacity-75\">Screenshots</a>
      <a href=\"#benefits\" class=\"hover:opacity-75\">Por que {esc(name)}</a>
      <a href=\"#faq\" class=\"hover:opacity-75\">FAQ</a>
    </nav>
    <div class=\"flex items-center gap-3\">
      <button onclick=\"toggleTheme()\" aria-label=\"Cambiar tema\" class=\"w-9 h-9 rounded-full border border-slate-200 dark:border-slate-700 flex items-center justify-center\">
        <svg xmlns='http://www.w3.org/2000/svg' class='w-4 h-4' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'><path stroke-linecap='round' stroke-linejoin='round' d='M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M16 12a4 4 0 11-8 0 4 4 0 018 0z'/></svg>
      </button>
      <a href=\"{esc(play_url)}\" class=\"hidden sm:inline-flex btn-primary text-sm font-semibold px-4 py-2 rounded-lg\">Descargar</a>
    </div>
  </div>
</header>

<section class=\"relative overflow-hidden\">
  <div class=\"hero-glow absolute inset-0 -z-0\"></div>
  <div class=\"max-w-6xl mx-auto px-4 pt-16 pb-20 grid md:grid-cols-2 gap-12 items-center relative z-10\">
    <div>
      <span class=\"inline-block text-xs font-semibold px-3 py-1 rounded-full badge-cat mb-4\">{esc(cat)}</span>
      <h1 class=\"text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white\">{esc(name)}</h1>
      <p class=\"mt-4 text-xl text-slate-600 dark:text-slate-300\">{esc(tagline)}</p>
      <p class=\"mt-6 text-slate-600 dark:text-slate-300 leading-relaxed\">{esc(desc)}</p>
      <div class=\"mt-8 flex flex-wrap gap-3\">
        <a href=\"{esc(play_url)}\" class=\"btn-primary inline-flex items-center gap-2 font-semibold px-6 py-3 rounded-xl shadow-lg\">
          <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' class='w-5 h-5' fill='currentColor'><path d='M3.6 2.2C3.2 2.5 3 3 3 3.7v16.6c0 .7.2 1.2.6 1.5L14 12 3.6 2.2zm11.7 9.2l3.2 1.8 2.4 1.4c1 .6 1 2 0 2.6l-2.4 1.4-3.5 2-3.1-2.8 3.4-6.4zm0-.8l-3.4-6.4 3.1-2.8 3.5 2 2.4 1.4c1 .6 1 2 0 2.6l-2.4 1.4-3.2 1.8z'/></svg>
          Descargar en Play Store
        </a>
        <a href=\"#features\" class=\"inline-flex items-center gap-2 font-semibold px-6 py-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700\">
          Ver caracteristicas
        </a>
      </div>
      <p class=\"mt-4 text-xs text-slate-500\">Desarrollado por DreamLabsTech</p>
    </div>
    <div class=\"flex justify-center\">
      <div class=\"w-40 h-40 md:w-56 md:h-56\">
        {APP_ICON_SVG.format(primary=primary, accent=accent, letter=letter)}
      </div>
    </div>
  </div>
</section>

<section id=\"features\" class=\"py-20 bg-white dark:bg-slate-900\">
  <div class=\"max-w-6xl mx-auto px-4\">
    <div class=\"max-w-2xl mb-12\">
      <h2 class=\"text-3xl font-extrabold text-slate-900 dark:text-white\">Caracteristicas principales</h2>
      <p class=\"mt-3 text-slate-600 dark:text-slate-300\">Todo lo que necesitas en {esc(name)} para sacarle el maximo a la categoria {esc(cat)}.</p>
    </div>
    <div class=\"grid md:grid-cols-2 lg:grid-cols-3 gap-6\">
      {feature_html}
    </div>
  </div>
</section>

<section id=\"screens\" class=\"py-20\">
  <div class=\"max-w-6xl mx-auto px-4\">
    <div class=\"max-w-2xl mb-12\">
      <h2 class=\"text-3xl font-extrabold text-slate-900 dark:text-white\">Un vistazo a {esc(name)}</h2>
      <p class=\"mt-3 text-slate-600 dark:text-slate-300\">Interfaz clara, animaciones suaves y flujos pensados para moverte rapido.</p>
    </div>
    <div class=\"grid grid-cols-1 md:grid-cols-3 gap-6\">
      {screens}
    </div>
  </div>
</section>

<section id=\"benefits\" class=\"py-20 bg-white dark:bg-slate-900\">
  <div class=\"max-w-6xl mx-auto px-4\">
    <div class=\"max-w-2xl mb-12\">
      <h2 class=\"text-3xl font-extrabold text-slate-900 dark:text-white\">Por que elegir {esc(name)}?</h2>
      <p class=\"mt-3 text-slate-600 dark:text-slate-300\">Disenada con criterios profesionales y pensamiento de producto, no con plantillas genericas.</p>
    </div>
    <div class=\"grid md:grid-cols-3 gap-6\">
      {benefit_html}
    </div>
  </div>
</section>

<section id=\"faq\" class=\"py-20\">
  <div class=\"max-w-3xl mx-auto px-4\">
    <h2 class=\"text-3xl font-extrabold text-slate-900 dark:text-white mb-8\">Preguntas frecuentes</h2>
    <div class=\"space-y-3\">
      {faq_html}
    </div>
  </div>
</section>

<section class=\"py-20\" style=\"background:linear-gradient(135deg,{primary},{accent})\">
  <div class=\"max-w-4xl mx-auto px-4 text-center text-white\">
    <h2 class=\"text-3xl md:text-4xl font-extrabold\">Empieza hoy con {esc(name)}</h2>
    <p class=\"mt-3 opacity-90\">Instala la app, activa el modo que prefieras y empieza a ver resultados desde el primer dia.</p>
    <a href=\"{esc(play_url)}\" class=\"mt-6 inline-flex items-center gap-2 bg-white text-slate-900 font-semibold px-6 py-3 rounded-xl shadow-lg hover:bg-slate-100\">
      <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' class='w-5 h-5' fill='currentColor'><path d='M3.6 2.2C3.2 2.5 3 3 3 3.7v16.6c0 .7.2 1.2.6 1.5L14 12 3.6 2.2z'/></svg>
      Descargar en Play Store
    </a>
  </div>
</section>

<footer class=\"bg-slate-900 text-slate-300 py-12\">
  <div class=\"max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-8\">
    <div>
      <div class=\"flex items-center gap-3\">
        <span class=\"w-9 h-9 rounded-xl flex items-center justify-center text-white font-bold\" style=\"background:linear-gradient(135deg,{primary},{accent})\">{letter}</span>
        <span class=\"text-white font-bold\">{esc(name)}</span>
      </div>
      <p class=\"mt-4 text-sm opacity-80\">Una app de DreamLabsTech. Creamos productos moviles con cuidado por la experiencia y la privacidad.</p>
    </div>
    <div>
      <h5 class=\"text-white font-semibold mb-3\">Enlaces</h5>
      <ul class=\"space-y-2 text-sm\">
        <li><a href=\"../index.html\" class=\"hover:underline\">Todas las apps</a></li>
        <li><a href=\"#features\" class=\"hover:underline\">Caracteristicas</a></li>
        <li><a href=\"#faq\" class=\"hover:underline\">FAQ</a></li>
        <li><a href=\"../privacy.html\" class=\"hover:underline\">Politica de privacidad</a></li>
      </ul>
    </div>
    <div>
      <h5 class=\"text-white font-semibold mb-3\">Contacto</h5>
      <ul class=\"space-y-2 text-sm opacity-80\">
        <li>contacto@dreamlabstech.io</li>
        <li>soporte@dreamlabstech.io</li>
        <li>&copy; 2026 DreamLabsTech. Todos los derechos reservados.</li>
      </ul>
    </div>
  </div>
</footer>

<script>
function toggleTheme() {{
  const html = document.documentElement;
  html.classList.toggle('dark');
  localStorage.setItem('dlt-theme', html.classList.contains('dark') ? 'dark' : 'light');
}}
</script>
</body>
</html>
"""


def index_page(apps: list) -> str:
    cards = []
    for a in apps:
        primary, accent = a["primary"], a["accent"]
        letter = (a["name"][:1] or "A").upper()
        cards.append(f"""
    <article class=\"app-card bg-white dark:bg-slate-800 rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all border border-slate-200 dark:border-slate-700\" data-name=\"{esc(a['name'].lower())}\" data-category=\"{esc(a['category'])}\">
      <div class=\"p-6\">
        <div class=\"flex items-center gap-4 mb-4\">
          <span class=\"w-14 h-14 rounded-2xl flex items-center justify-center text-white font-extrabold text-xl\" style=\"background:linear-gradient(135deg,{primary},{accent})\">{letter}</span>
          <div>
            <h3 class=\"font-bold text-lg text-slate-900 dark:text-white leading-tight\">{esc(a['name'])}</h3>
            <span class=\"inline-block text-[11px] font-semibold mt-1 px-2 py-0.5 rounded-full\" style=\"background:{hex_rgba(primary,0.15)};color:{primary}\">{esc(a['category'])}</span>
          </div>
        </div>
        <p class=\"text-sm text-slate-600 dark:text-slate-300 leading-relaxed line-clamp-3\">{esc(a['tagline'])}</p>
        <a href=\"apps/{esc(a['slug'])}.html\" class=\"mt-4 inline-flex items-center gap-1 font-semibold text-sm\" style=\"color:{primary}\">
          Ver mas
          <svg xmlns='http://www.w3.org/2000/svg' class='w-4 h-4' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'><path stroke-linecap='round' stroke-linejoin='round' d='M9 5l7 7-7 7'/></svg>
        </a>
      </div>
    </article>""")

    category_buttons = "".join(
        f'<button class="cat-btn px-4 py-2 rounded-full text-sm font-semibold border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700" data-cat="{esc(c)}">{esc(c)}</button>'
        for c in CATEGORIES
    )

    return f"""<!doctype html>
<html lang=\"es\" class=\"scroll-smooth\">
<head>
<meta charset=\"utf-8\"/>
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
<title>DreamLabsTech - 120 Apps Revolucionarias</title>
<meta name=\"description\" content=\"Explora el catalogo de 120+ apps moviles de DreamLabsTech: salud mental, fitness, finanzas, productividad, educacion y mucho mas.\"/>
<script src=\"https://cdn.tailwindcss.com\"></script>
<script>
  tailwind.config = {{ darkMode: 'class' }};
  (function () {{
    const saved = localStorage.getItem('dlt-theme');
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'dark' || (!saved && systemDark)) document.documentElement.classList.add('dark');
  }})();
</script>
<style>
  body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
  .line-clamp-3 {{ display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
  .hero-bg {{ background: radial-gradient(1200px 600px at 10% -10%, rgba(124,58,237,0.25), transparent), radial-gradient(900px 500px at 90% -20%, rgba(14,165,233,0.25), transparent); }}
  .cat-btn.active {{ background: #111827; color: white; border-color: #111827; }}
  .dark .cat-btn.active {{ background: #f8fafc; color: #0f172a; border-color: #f8fafc; }}
</style>
</head>
<body class=\"bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100\">

<header class=\"sticky top-0 z-30 backdrop-blur bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800\">
  <div class=\"max-w-6xl mx-auto px-4 h-16 flex items-center justify-between\">
    <a href=\"#top\" class=\"flex items-center gap-3\">
      <span class=\"w-9 h-9 rounded-xl flex items-center justify-center text-white font-extrabold\" style=\"background:linear-gradient(135deg,#7C3AED,#06B6D4)\">D</span>
      <span class=\"font-extrabold text-slate-900 dark:text-white\">DreamLabsTech</span>
    </a>
    <nav class=\"hidden md:flex gap-6 text-sm font-medium\">
      <a href=\"#catalog\" class=\"hover:opacity-75\">Catalogo</a>
      <a href=\"#categories\" class=\"hover:opacity-75\">Categorias</a>
      <a href=\"#contact\" class=\"hover:opacity-75\">Contacto</a>
    </nav>
    <div class=\"flex items-center gap-2\">
      <button onclick=\"toggleTheme()\" aria-label=\"Cambiar tema\" class=\"w-9 h-9 rounded-full border border-slate-200 dark:border-slate-700 flex items-center justify-center\">
        <svg xmlns='http://www.w3.org/2000/svg' class='w-4 h-4' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'><path stroke-linecap='round' stroke-linejoin='round' d='M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M16 12a4 4 0 11-8 0 4 4 0 018 0z'/></svg>
      </button>
    </div>
  </div>
</header>

<section id=\"top\" class=\"hero-bg\">
  <div class=\"max-w-6xl mx-auto px-4 py-20 md:py-28\">
    <div class=\"max-w-3xl\">
      <span class=\"inline-block text-xs font-semibold px-3 py-1 rounded-full bg-violet-100 text-violet-700 dark:bg-violet-500/20 dark:text-violet-300\">Catalogo oficial - 2026</span>
      <h1 class=\"mt-4 text-4xl md:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight\">DreamLabsTech<br/><span class=\"bg-gradient-to-r from-violet-500 via-fuchsia-500 to-cyan-500 bg-clip-text text-transparent\">120 Apps Revolucionarias</span></h1>
      <p class=\"mt-6 text-lg md:text-xl text-slate-600 dark:text-slate-300\">Productos moviles cuidadosamente disenados en 13 categorias: bienestar, fitness, finanzas, productividad y mucho mas. Una suite completa para acompanarte cada dia.</p>
      <div class=\"mt-8 flex flex-wrap gap-3\">
        <a href=\"#catalog\" class=\"inline-flex items-center gap-2 bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-semibold px-6 py-3 rounded-xl shadow-lg\">
          Explorar apps
          <svg xmlns='http://www.w3.org/2000/svg' class='w-4 h-4' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'><path stroke-linecap='round' stroke-linejoin='round' d='M9 5l7 7-7 7'/></svg>
        </a>
        <a href=\"#categories\" class=\"inline-flex items-center gap-2 font-semibold px-6 py-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800\">
          Ver categorias
        </a>
      </div>
    </div>
  </div>
</section>

<section id=\"categories\" class=\"py-10\">
  <div class=\"max-w-6xl mx-auto px-4\">
    <div class=\"flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6\">
      <div>
        <h2 class=\"text-2xl font-extrabold text-slate-900 dark:text-white\">Catalogo completo</h2>
        <p class=\"text-sm text-slate-600 dark:text-slate-300\">Filtra por categoria o busca por nombre. {len(apps)} apps disponibles.</p>
      </div>
      <div class=\"relative w-full md:w-80\">
        <input id=\"search\" type=\"search\" placeholder=\"Buscar app...\" class=\"w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-400\"/>
        <svg xmlns='http://www.w3.org/2000/svg' class='w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'><path stroke-linecap='round' stroke-linejoin='round' d='M21 21l-4.3-4.3M10 18a8 8 0 118-8 8 8 0 01-8 8z'/></svg>
      </div>
    </div>
    <div class=\"flex flex-wrap gap-2\">
      <button class=\"cat-btn active px-4 py-2 rounded-full text-sm font-semibold border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700\" data-cat=\"all\">Todas</button>
      {category_buttons}
    </div>
  </div>
</section>

<section id=\"catalog\" class=\"pb-24\">
  <div class=\"max-w-6xl mx-auto px-4\">
    <div id=\"grid\" class=\"grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6\">
      {''.join(cards)}
    </div>
    <p id=\"empty\" class=\"hidden text-center text-slate-500 py-12\">No encontramos apps con esos criterios.</p>
  </div>
</section>

<footer id=\"contact\" class=\"bg-slate-900 text-slate-300 py-12\">
  <div class=\"max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-8\">
    <div>
      <div class=\"flex items-center gap-3\">
        <span class=\"w-9 h-9 rounded-xl flex items-center justify-center text-white font-extrabold\" style=\"background:linear-gradient(135deg,#7C3AED,#06B6D4)\">D</span>
        <span class=\"text-white font-extrabold\">DreamLabsTech</span>
      </div>
      <p class=\"mt-4 text-sm opacity-80\">Estudio de producto movil enfocado en experiencia, calidad y privacidad.</p>
    </div>
    <div>
      <h5 class=\"text-white font-semibold mb-3\">Catalogo</h5>
      <ul class=\"space-y-2 text-sm\">
        <li><a href=\"#catalog\" class=\"hover:underline\">Todas las apps</a></li>
        <li><a href=\"#categories\" class=\"hover:underline\">Categorias</a></li>
        <li><a href=\"./privacy.html\" class=\"hover:underline\">Politica de privacidad</a></li>
      </ul>
    </div>
    <div>
      <h5 class=\"text-white font-semibold mb-3\">Contacto</h5>
      <ul class=\"space-y-2 text-sm opacity-80\">
        <li>contacto@dreamlabstech.io</li>
        <li>soporte@dreamlabstech.io</li>
        <li>&copy; 2026 DreamLabsTech. Todos los derechos reservados.</li>
      </ul>
    </div>
  </div>
</footer>

<script>
const cards = Array.from(document.querySelectorAll('.app-card'));
const search = document.getElementById('search');
const empty = document.getElementById('empty');
let activeCat = 'all';

function applyFilters() {{
  const q = (search.value || '').toLowerCase();
  let visible = 0;
  cards.forEach(c => {{
    const name = c.dataset.name;
    const cat = c.dataset.category;
    const matchesCat = activeCat === 'all' || cat === activeCat;
    const matchesQuery = !q || name.includes(q);
    const show = matchesCat && matchesQuery;
    c.style.display = show ? '' : 'none';
    if (show) visible++;
  }});
  empty.classList.toggle('hidden', visible > 0);
}}

document.querySelectorAll('.cat-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeCat = btn.dataset.cat;
    applyFilters();
  }});
}});
search.addEventListener('input', applyFilters);

function toggleTheme() {{
  const html = document.documentElement;
  html.classList.toggle('dark');
  localStorage.setItem('dlt-theme', html.classList.contains('dark') ? 'dark' : 'light');
}}
</script>
</body>
</html>
"""


PRIVACY_PAGE = """<!doctype html>
<html lang=\"es\" class=\"scroll-smooth\">
<head>
<meta charset=\"utf-8\"/>
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>
<title>Politica de privacidad | DreamLabsTech</title>
<script src=\"https://cdn.tailwindcss.com\"></script>
</head>
<body class=\"bg-slate-50 text-slate-800\">
<main class=\"max-w-3xl mx-auto px-4 py-16\">
  <a href=\"./index.html\" class=\"text-sm text-violet-600 hover:underline\">&larr; Volver al catalogo</a>
  <h1 class=\"text-3xl font-extrabold mt-4 mb-6\">Politica de privacidad</h1>
  <p class=\"mb-4\">DreamLabsTech respeta tu privacidad. Nuestras aplicaciones estan disenadas para minimizar la recoleccion de datos y darte control total sobre tu informacion.</p>
  <h2 class=\"text-xl font-bold mt-8 mb-3\">Datos que recopilamos</h2>
  <p class=\"mb-4\">La mayoria de nuestras apps funcionan completamente en tu dispositivo. Cuando se requiere sincronizacion, se cifran los datos en transito y se almacenan de forma segura.</p>
  <h2 class=\"text-xl font-bold mt-8 mb-3\">Publicidad y analiticas</h2>
  <p class=\"mb-4\">Podemos usar proveedores de analiticas anonimizadas y publicidad no intrusiva. Ofrecemos controles claros para optar por no participar.</p>
  <h2 class=\"text-xl font-bold mt-8 mb-3\">Contacto</h2>
  <p>Para cualquier consulta escribe a <a class=\"text-violet-600 hover:underline\" href=\"mailto:privacy@dreamlabstech.io\">privacy@dreamlabstech.io</a>.</p>
</main>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    apps = []
    # File may contain stray bare \r characters. Read raw bytes and split
    # only on \n after normalizing line endings.
    with open(INVENTORY, "rb") as fh:
        raw = fh.read().decode("utf-8", errors="replace")
    raw = raw.replace("\r\n", "\n").replace("\r", "")
    for line in raw.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 4:
            continue
        slug_raw, pkg, raw_cat, desc = parts[0].strip(), parts[1].strip(), parts[2].strip(), "|".join(parts[3:]).strip()
        if not slug_raw:
            continue
        slug = slugify(slug_raw)
        cat = classify(slug_raw, raw_cat, desc)
        display_name, display_tag = DISPLAY.get(slug_raw, (pretty_name(slug_raw), None))
        if not display_name:
            display_name = pretty_name(slug_raw) or slug_raw or "App"
        if not display_tag:
            display_tag = {
                "Salud Mental": "Bienestar mental simple y respetuoso",
                "Fitness": "Tu entrenador personal en el bolsillo",
                "Finanzas": "Control financiero claro y privado",
                "Alimentacion": "Come mejor sin complicaciones",
                "Productividad": "Organiza tu dia con enfoque real",
                "Educacion": "Aprende a tu ritmo, cada dia",
                "Estilo de Vida": "Pequenos habitos que suman",
                "Musica": "Experiencia musical profesional",
                "Herramientas": "Medicion y utilidades precisas",
                "Social": "Conecta de forma segura y clara",
                "Ecommerce": "Compra y vende con confianza",
                "Juegos": "Diversion inmediata y justa",
                "Negocios": "Digitaliza tu operacion con agilidad",
            }.get(cat, "App de DreamLabsTech")
        primary, accent = PALETTE[cat]
        description = normalize_description(desc, cat, display_name)
        apps.append({
            "slug": slug,
            "name": display_name,
            "package": pkg,
            "category": cat,
            "tagline": display_tag,
            "description": description,
            "primary": primary,
            "accent": accent,
            "play_url": PLAY_STORE_TMPL.format(pkg=pkg),
        })

    # Write per-app pages
    for a in apps:
        out = APPS_DIR / f"{a['slug']}.html"
        out.write_text(app_page(a), encoding="utf-8")

    # Sort index by category then name for stable output
    apps_sorted = sorted(apps, key=lambda x: (CATEGORIES.index(x["category"]), x["name"].lower()))
    (BASE / "index.html").write_text(index_page(apps_sorted), encoding="utf-8")
    (BASE / "privacy.html").write_text(PRIVACY_PAGE, encoding="utf-8")

    print(f"Wrote {len(apps)} app pages + index.html + privacy.html")
    # Category breakdown
    counts = {}
    for a in apps:
        counts[a["category"]] = counts.get(a["category"], 0) + 1
    for c in CATEGORIES:
        print(f"  {c}: {counts.get(c, 0)}")


if __name__ == "__main__":
    main()
