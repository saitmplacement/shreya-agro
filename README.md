# Shreya Agro Foods — Website

Static B2B catalogue site for **Shreya Agro Foods Ltd.** (Mumbai). Plain HTML + CSS + vanilla JS — no PHP, no database, no admin panel. Every product and CTA leads to an enquiry form (no cart, no prices).

Built to the "On-Page SEO & Website Performance Guidelines" and the page designs in the project brief (Home, About, Products + product pages, Vendor, Contact & Careers, 404).

## Pages

| URL | Page |
| --- | --- |
| `/` | Home |
| `/about-us/` | About (hero, intro, vision/mission, why us, journey timeline, quality, B2B CTA) |
| `/products/` | Products (hero, categories, search + category/sub-category filters, product grid, CTA) |
| `/products/<slug>/` | 18 product pages (gallery, spec table, why choose, related, enquiry), grouped into 8 categories |
| `/vendor/` | Vendor / B2B partner page with partner form + brochure download |
| `/contact-us/` | Contact + Careers combined (enquiry form, openings, application popup, map) |
| `/careers/` | Short URL → redirects to `/contact-us/#careers` |
| `404.html` | Custom 404 (served with a real 404 status via `.htaccess`) |

Home also has the rotating "From India to the World" country circle (CSS animation; flags come from the MIT-licensed `flag-icons` set in `assets/flags/`). Site-wide: sticky header, green chatbot (Product Enquiry / B2B Partnership / Become a Distributor / Careers / Talk to Our Team), B2B enquiry popup that auto-fills "Enquiry For: <product>".

## Stack & conventions

- **Fonts (self-hosted, `font-display: swap`):** Plus Jakarta Sans for UI/body text, Playfair Display for headings and Great Vibes for the script accent (e.g. "Under One Roof") — as in the approved mockups. To go back to a single font, remove the two extra `@font-face` blocks and `--font-display` in `tools/src/style.css`.
- **Images:** WebP only, responsive (`srcset`/`sizes`), explicit width/height, lazy-loaded below the fold; hero is eager + preloaded. Descriptive names: `shreya-agro-foods-<name>-<width>.webp`. Social-share images live in `assets/images/og/` (1200×630 JPG).
- **SEO:** unique title/description/canonical/OG per page, one H1, Organization + WebSite (home), Product + BreadcrumbList (product pages), LocalBusiness (contact), `sitemap.xml`, `robots.txt`, HTTPS + www redirect in `.htaccess`.
- **Colour:** deep green + lime accent on cream/white; the 8 category cards use soft pastel tints (as in the mockup).

## Editing content (source of truth)

All pages are generated from one script so header/footer/modals/chatbot stay identical everywhere.

```bash
python3 tools/build.py      # needs Python 3 + Pillow; writes the HTML, CSS, JS, sitemap, robots, .htaccess
```

- **Products, categories, job openings, company details** → top of `tools/build.py` (`PRODUCTS`, `CATEGORIES`, `JOBS`, address/phone/email constants).
- **Styles** → `tools/src/style.css` · **Scripts** → `tools/src/main.js` (the build minifies them into `assets/css/style.css` and `assets/js/main.js`; if `esbuild` is installed or `$ESBUILD` points to it, JS is minified too).
- **Add a product:** add an entry to `PRODUCTS`, add its images (see below), run the build — the product page, listing card, sitemap entry and related-products links are generated.
- **Add / remove a job:** edit `JOBS` (an empty list shows the "No Current Openings" state with "Send Your Resume").
- **New images:** drop the original into any folder, add it to `SOURCES` in `tools/optimize_images.py`, and run `python3 tools/optimize_images.py <source-dir>` (resizes to WebP + creates the OG JPG).

Never edit the generated `*.html` files by hand — your changes will be overwritten by the next build.

## Settings you must fill in before launch — `assets/js/config.js`

This one small file is **not** generated; edit it directly (no rebuild needed):

```js
window.SHREYA_CONFIG = {
  web3formsKey: "",   // free key from https://web3forms.com (enter your email, key arrives instantly)
  gaId: "",           // Google Analytics 4 ID, e.g. "G-XXXXXXXXXX"
  ...
};
```

- **Forms:** with a Web3Forms key, enquiry / partner / contact / job-application forms email the submission to you. **Until a key is set, forms fall back to opening the visitor's email app** with the enquiry pre-filled (the success message says so honestly). Resume *attachments* need Web3Forms' paid plan; on the free plan the application arrives as text.
- **Analytics:** with a GA4 ID the site tracks `view_item` (product views), `enquiry_click`, `generate_lead` (form submissions), `career_apply_click`, `career_application`, `b2b_partner_enquiry`, `phone_click`, `whatsapp_click`, `email_click`. Without an ID nothing is loaded.

## Deploy (Hostinger / any static host)

1. Upload the repository contents to `public_html` (hPanel → Git, or upload a ZIP). `tools/` is not needed on the server but harmless.
2. Enable SSL; `.htaccess` forces HTTPS and the `www.` host (matching the canonical URLs). If you prefer the non-www host, change `DOMAIN` in `tools/build.py`, the rewrite rule in `HTACCESS`, and rebuild.
3. Set `assets/js/config.js` (above).
4. Search Console: verify the domain, submit `https://www.shreyaagrofoods.com/sitemap.xml`, request indexing for key pages.

## Still open (needs input from the client)

- YouTube channel link (footer currently shows Facebook, Instagram, LinkedIn only).
- Real photography from the shared Drive product folder, if it differs from the images already in the repo.
- Final Google Maps pin / place link if a verified listing exists (the map currently searches the registered address).

## Testing notes

The site was tested in headless Chromium at desktop (1366) and mobile (390) with real clicks, plus an overflow sweep from 320 px to 1920 px: nav, enquiry/apply modals, validation, success and failure states, filters, gallery, chatbot, anchors, 404. Core Web Vitals on localhost: LCP < 0.2 s, CLS 0 (re-check on the live host with PageSpeed Insights).
