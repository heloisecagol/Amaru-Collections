# Amaru Collections — pre-sale site

Static site (HTML / CSS / vanilla JS, no build step) + Supabase for the waitlist.
Stripe Checkout will be added with the shop pages via a small Supabase Edge Function.

```
site/
  index.html            Landing page
  css/styles.css        All styles (colour tokens at the top)
  js/config.js          Supabase keys, Instagram, email  ← fill in
  js/products.js        The seven earrings (names, prices, sources)  ← fill in
  js/layout.js          Shared navigation + footer (edit once, applies everywhere)
  js/main.js            Nav, menu, reveal/parallax, collection grid, waitlist form
  assets/earrings/      earring-01.png … earring-06.png (transparent cut-outs)
  assets/og/            Share image for Instagram / WhatsApp (1200×630)
supabase/schema.sql     Waitlist table + security rules
```

## Preview locally

```bash
python3 -m http.server 8080 --directory site
```

Then open http://localhost:8080

## Connect the waitlist to Supabase

1. Create a Supabase project.
2. SQL Editor → paste `supabase/schema.sql` → Run.
3. Settings → API → copy the Project URL and the `anon` public key into `site/js/config.js`.

Until step 3 is done, sign-ups are kept in the browser's localStorage only (for testing).
Sign-ups appear under Table Editor → `waitlist`.

## Placeholders

Search the project for `PLACEHOLDER` and `your-domain.example` to find everything that still needs real details.

## Languages

English only for now. Strings for the nav/footer live in `js/layout.js` and product text in
`js/products.js`, both keyed by locale. French and Spanish pages will go in `site/fr/` and `site/es/`
with `hreflang` links.
