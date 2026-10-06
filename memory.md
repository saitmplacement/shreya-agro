# Shreya Agro Foods — Project Memory

Quick orientation for anyone (human or AI) picking this project up. See `README.md` for the full guide.

## What this is
Fully static B2B catalogue website for Shreya Agro Foods Ltd. (Mumbai). Goal: fast, SEO-optimised lead generation — no cart, no prices, every CTA ends in an enquiry form.

## Architecture
- **Generated site.** `tools/build.py` is the single source of truth for all HTML (header, footer, modals, chatbot, every page, sitemap, robots, `.htaccess`). Output is committed to the repo root so the host only serves static files.
- **Sources:** `tools/src/style.css`, `tools/src/main.js` (minified into `assets/css/style.css`, `assets/js/main.js`). Images: `tools/optimize_images.py` (originals → responsive WebP + OG JPG).
- **Hand-edited file:** `assets/js/config.js` (Web3Forms key, GA4 ID, contact constants) — not overwritten by the build once it exists.
- Do not edit generated HTML by hand.

## Brief → implementation map
- Nav: Home | About Us | Products | Vendor | Contact Us (+ Enquire Now). Careers lives inside Contact (`/contact-us/#careers`); `/careers/` redirects there.
- Fonts: Plus Jakarta Sans (body/UI) + Playfair Display (headings) + Great Vibes (script accent), matching the mockups. Palette: deep green, lime accent, cream backgrounds, pastel category tints.
- Products page = hero → categories → search/filter/grid → B2B CTA. Product page = breadcrumb → gallery + info table → why choose → related → CTA. Enquiry popup shows "Enquiry For: <product>".
- Chatbot: guided menu (no fake AI replies) → opens forms, links, call/WhatsApp/email.

## Key facts
- Domain/canonical: `https://www.shreyaagrofoods.com` (HTTPS + www enforced in `.htaccess`).
- Registered office: 411-412, Mastermind Rd, Royal Palms, Aarey Milk Colony, Goregaon East, Mumbai 400065. Phone +91 70586 74452. Email info@shreyaagrofoods.com. Hours Mon–Fri 10–6, Sat 10–2.
- Forms: Web3Forms when `web3formsKey` is set, otherwise a `mailto:` fallback.

## Pending
- Web3Forms key + GA4 ID in `assets/js/config.js`.
- YouTube link, Search Console verification + sitemap submission.
- Delete legacy files that the rebuild superseded (see PR notes): old PNGs in `assets/images/products/`, `assets/images.zip`, old `*.py` helper scripts, root `vendor.html`, and the product folders no longer in the sitemap.
