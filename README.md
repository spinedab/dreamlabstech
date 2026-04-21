# DreamLabsTech Landing Pages

Static landing-page catalog for 126 DreamLabsTech mobile apps, auto-generated
from `/tmp/apps_inventory.txt`.

## What's inside

```
landing-pages/
  index.html          # master catalog with search + category filter
  privacy.html        # shared privacy policy
  generate.py         # generator script (single source of truth)
  apps/               # 126 per-app landing pages
    <app_slug>.html
  assets/             # (reserved for images you add later)
```

Every page is a self-contained HTML file. Styling comes from the
Tailwind CSS Play CDN (`https://cdn.tailwindcss.com`) — no build step
is required.

## Regenerating

The generator is idempotent. Edit `/tmp/apps_inventory.txt` (or the
display/category maps inside `generate.py`) and run:

```bash
cd landing-pages
python3 generate.py
```

This rewrites `index.html`, `privacy.html` and every file under
`apps/`. Output is deterministic so the result is safe to commit.

### Inventory format

One app per line in `/tmp/apps_inventory.txt`:

```
<slug>|<package_id>|<raw_category>|<description>
```

`raw_category` is taken from the directory the Flutter project lives
under (e.g. `Mobile-Apps`, `Musica`, `Ecommerce-Negocios`, ...).
The generator maps it to one of 13 user-facing categories using the
`SLUG_CATEGORY` override map and a heuristic fallback.

## Deployment

The site is fully static. Deploy the entire `landing-pages/` directory to
any host:

### GitHub Pages
1. Push `landing-pages/` to a repository.
2. Enable Pages, pointing it at either the root of `main` (with a `CNAME`
   that maps the folder) or to `/docs` after renaming, or at
   `landing-pages/` via a GitHub Action.

### Netlify / Vercel / Cloudflare Pages
Drag-and-drop the folder, or connect the repo and set
`landing-pages/` as the publish directory with no build command.

### Plain HTTP server
```bash
cd landing-pages
python3 -m http.server 8080
# then open http://localhost:8080
```

## Adding a new app

1. Append a row to `/tmp/apps_inventory.txt`.
2. (Optional) Add a Spanish display name + tagline in the `DISPLAY`
   dict inside `generate.py`.
3. (Optional) Force a category with `SLUG_CATEGORY[slug] = "..."`.
4. Run `python3 generate.py`.

## Customization

- **Categories**: `CATEGORIES` list controls index filter order.
- **Colors**: `PALETTE` maps each category to a primary + accent hex pair.
- **Features / Benefits / FAQ copy**: `CAT_FEATURES`, `CAT_BENEFITS`,
  `CAT_FAQ` hold the Spanish copy bank per category.
- **Play Store URLs**: built from `package_id` via `PLAY_STORE_TMPL`.

## Notes

- No build system, no npm, no bundler. Tailwind runs at runtime via CDN.
- All pages respect system dark mode and remember the user's choice
  via `localStorage` (`dlt-theme`).
- Icons and screenshots are inline SVG placeholders coloured per app —
  replace them by adding real assets to `assets/` and updating
  `APP_ICON_SVG` / `build_screens_svg` in `generate.py`.
