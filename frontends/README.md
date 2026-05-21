# Reference Frontends

Three static frontends, one per domain option in the assignment. Each one is
plain HTML + CSS + a single `app.js` — no build step, no framework, no
package manager.

```
frontends/
├── tickets/         # Option A — concert ticketing  (brutalist gig-poster)
├── conference/      # Option B — conference sessions (editorial / magazine)
└── reservations/    # Option C — restaurant tables   (warm hospitality)
```

## Running locally

Pick the one that matches the domain you chose and serve the folder. Any
static server will do — Python's built-in works fine:

```bash
cd frontends/tickets   # or conference / reservations
python3 -m http.server 8080
```

Open `http://localhost:8080`.

## Pointing it at your API

By default each frontend calls `/api/v1/...` on the same origin. Two ways to
hook it up to your service:

1. **Through Nginx** (recommended, matches the assignment) — serve the
   frontend folder as the `/` location in your Nginx config, and proxy
   `/api/` to your FastAPI container. This is exactly the topology the
   reviewer will use.

2. **Cross-origin during development** — override the base URL from the
   browser console before reloading the page:

   ```js
   // tickets
   localStorage; // (just so the DevTools console is open)
   window.LOUD_API_BASE = 'http://localhost:8000/api/v1';
   // conference
   window.SYMPOSIUM_API_BASE = 'http://localhost:8000/api/v1';
   // reservations
   window.MESA_API_BASE = 'http://localhost:8000/api/v1';
   ```

   You'll need to enable CORS on your FastAPI service for the dev origin.

All three frontends:

- Call `/api/v1/healthz` every 15 seconds and show a status dot in the footer.
- Degrade gracefully — if a fetch fails they show a calm error message in
  the corresponding section rather than throwing.
- Open a `<dialog>` for the detail view (no router, no SPA).

## What you must NOT do

- Don't introduce a framework. Don't add a bundler.
- Don't rewrite the API contract just because it's easier in your service —
  the frontend is the source of truth. Fix the service.
- Don't bake your domain logic into the JS. Computing availability,
  applying pricing tiers, filtering by timezone — all of that runs server
  side. The JS is a thin presentation layer on purpose.
- Don't modify any of these files for your submission