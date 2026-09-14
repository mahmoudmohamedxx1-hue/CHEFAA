# The Pharmacy — Deployment & Operations Guide

## 1. Opening the Admin Panel

1. Open **`/admin`** on your site (e.g. `https://your-domain.com/admin`)
2. If you are not logged in as an admin you will see an access-restricted screen with a **Login** button
3. Log in with the admin account:

   | Field | Value |
   |---|---|
   | Email | `admin@thepharmacy.com` |
   | Password | `Admin@2026` |

4. After login you are redirected back to the Admin Dashboard (products, orders, revenue, prescriptions, users)

> The admin link is also available from the account dropdown menu (top-left user icon) whenever you are logged in as an admin.

Demo customer account: `demo@thepharmacy.com` / `Demo@2026`

**Change the admin password before going live.** You can do it from the admin panel or with:

```bash
bunx tsx -e "
import { hash } from './src/lib/auth'
console.log(await hash('NEW_PASSWORD'))
" # then update the User row in the database
```

## 2. Pushing to GitHub

The project already has a local git repository (branch `main`). From the project root:

```bash
# 1. Create a new repo on github.com (no README, no .gitignore — we already have one)

# 2. Connect it (replace <USERNAME> and <REPO> with yours)
git remote add origin https://github.com/<USERNAME>/<REPO>.git

# 3. Push
git push -u origin main
```

If you cloned/copied this folder without git history, start fresh:

```bash
git init
git add -A
git commit -m "The Pharmacy — bilingual AI-powered e-pharmacy"
git branch -M main
git remote add origin https://github.com/<USERNAME>/<REPO>.git
git push -u origin main
```

What gets pushed: source code, `public/images` (product photos, ~18 MB), `db/custom.db` (seeded catalog, ~1 MB), scripts.
What stays out: `node_modules`, `.next`, `.env*`, dev logs (see `.gitignore`).

## 3. Deploying to Vercel

1. Push to GitHub (step 2)
2. On [vercel.com](https://vercel.com) → **Add New → Project** → import your repo
3. Framework preset: **Next.js** (auto-detected). Leave build settings default.
4. Add the environment variable:

   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_SITE_URL` | `https://your-domain.com` (used for SEO tags, sitemap, link previews) |

5. Deploy

### Important — SQLite on Vercel

The app currently uses a **SQLite file** (`db/custom.db`) committed to the repo. On Vercel:

- ✅ Browsing, search, AI features, admin login all work (read-only)
- ⚠️ **Writes (placing orders, registering users, admin edits) will NOT persist** — serverless functions have an ephemeral, read-only filesystem. Orders will appear to succeed but won't be saved.

For a real store, pick one:

| Option | Effort | Notes |
|---|---|---|
| **Turso** (libsql) | ~1 hour | SQLite-compatible, free tier, keeps current schema. Best path. |
| **Neon / Supabase** (Postgres) | ~half day | Change Prisma provider to `postgresql`, adjust a few column types. |
| **VPS** (Hetzner/DigitalOcean) | ~1 hour | Run `bun run build && bun run start` behind Caddy/Nginx. SQLite works fully as-is. |

Until then, the Vercel deployment is a fully browsable demo/staging site.

## 4. Local development

```bash
bun install
bun run dev        # http://localhost:3000
bun run lint       # ESLint
```

## 5. PWA (mobile app) verification

- **Android/Chrome**: open the site → browser menu shows "Install app" (or use the in-app "Install App" button in the side menu / footer)
- **iPhone/Safari**: open the site → Share → **Add to Home Screen** → it opens fullscreen like a native app (standalone mode, no browser bar, own splash screen and teal status bar)
- Test offline: load a few pages, enable airplane mode, reopen — visited pages still work (service worker cache)

PWA files: `public/manifest.webmanifest`, `public/sw.js`, icons in `public/icons/`.
Regenerate icons/splash screens: `python3 scripts/gen_pwa_assets.py`

## 6. Shareable links (URL map)

| Page | URL |
|---|---|
| Home | `/` |
| Category | `/category/vitamins` |
| Product | `/product/panadol-advance-500mg-24-tablets` |
| Search | `/search/panadol` |
| Prescription AI | `/prescription` |
| AI Assistant | `/assistant` |
| Interaction checker | `/interactions` |
| Cart / Checkout | `/cart`, `/checkout` |
| Order confirmation | `/order-success/<orderId>` |
| Account pages | `/login`, `/register`, `/orders`, `/account`, `/wishlist` |
| Admin | `/admin` |

Old hash links (`/#/p/<slug>`, `/#/c/<slug>`, …) are automatically redirected to the new clean URLs, so previously shared links keep working.
