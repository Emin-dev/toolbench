# Toolbench — backlog

Vetted, gate-passing tool ideas, most-ready first. Each is genuinely useful,
defensible, fully client-side (no backend / no paid API / no ads). The loop
takes the top item, builds it, verifies both layers, deploys, and lists it.

> Shipped tools move to `LEDGER.md`. Cut ideas are struck through with a reason.

## Ready to build

1. **ConsentLens** — GDPR cookie & tracker scanner.
   Paste a page's HTML → detects tracking scripts (GA, Meta Pixel, TikTok,
   Hotjar, …) and the cookies they set, flags which legally need prior consent,
   and whether a compliant consent banner is present. *Buyer:* small EU store
   owner unsure if they're breaking GDPR. *Defensible:* a real, maintained
   tracker/cookie signature map + plain-English legal framing, like AccessProof.
   *Tech:* client-side HTML parse. Pairs with AccessProof (compliance cluster).

2. **ShrinkRay** — private image compressor / resizer / converter.
   Drop JPG/PNG/WebP → compress, resize, convert, batch — 100% in the browser,
   nothing uploaded. *Buyer:* anyone who needs smaller images and doesn't want
   to upload private photos to a random site. *Defensible:* the privacy angle +
   real quality controls (target size, format, dimensions) beat upload-based
   tools. *Tech:* Canvas / `createImageBitmap`, download as zip.

3. **PocketPDF** — private PDF toolkit.
   Merge, split, reorder, rotate, and compress PDFs entirely in the browser.
   *Buyer:* people handling contracts/invoices who won't upload them to a
   stranger's server. *Defensible:* real PDF manipulation (vendored `pdf-lib`),
   offline + private. *Tech:* `pdf-lib` vendored, zero build step.

4. **SiteCheck** — on-page SEO & social-preview checker.
   Paste a page's HTML → checks title, meta description, Open Graph / Twitter
   cards, headings, canonical, structured-data basics, and shows exactly how the
   page previews on Google/Facebook/X, with plain-English fixes. *Buyer:* small
   business owner whose site "isn't showing up right". *Defensible:* real checks
   + a faithful preview renderer. Compliance/quality cluster.

5. **Invoicer** — freelancer invoice builder.
   Fill a short form → a clean, printable/PDF invoice; save client + item
   templates locally; EU-VAT aware. *Buyer:* freelancers / sole traders
   (incl. Azerbaijani fərdi sahibkar). *Defensible:* good UX, local persistence,
   correct tax/number handling. *Tech:* client-side, print-to-PDF or `pdf-lib`.

6. **PolicyDraft** — privacy & cookie policy generator.
   Answer a short questionnaire → a GDPR-aware privacy + cookie policy for a
   small store, export as HTML/text. Clearly "not legal advice". *Buyer:* small
   EU store owner who needs a policy page. *Defensible:* real, maintained
   clause logic mapped to what the site actually does. Compliance cluster.

7. **IconForge** — favicon & app-icon generator.
   Upload one image → all favicon sizes + Apple touch icons + a `manifest.json`,
   downloaded as a zip, client-side. *Buyer:* anyone launching a site/app.
   *Defensible:* completeness (every modern size + manifest) + privacy.

## Notes
- Compliance cluster (AccessProof, ConsentLens, SiteCheck, PolicyDraft) gives
  the bench a coherent, defensible identity: "keep your small online business
  legal, fast, and trustworthy" — plus broadly-useful private file tools.
- None of these hides a backend cost. If a future idea needs a server or paid
  API, it does NOT go here — it goes to the owner as a stop-and-ask.
