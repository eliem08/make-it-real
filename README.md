<!-- sell-kit:start -->
# Make It Real

[![CI](https://github.com/eliem08/make-it-real/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/make-it-real/actions/workflows/ci.yml)

> **Design a physical product with AI and get it made.**

**Who it's for:** Creators and small brands turning AI designs into merch, prints and 3D-printed parts.

**The problem:** AI designs look great on screen but fail at the factory: wrong DPI, too many colours, walls too thin, minimums too high.

**What you get:** Manufacturability checks and side-by-side quotes across print and 3D methods, then a production order (via the Python API) for the chosen option.

## Quickstart

Customers receive a release archive with the wheel and the examples. Python 3.10+ and no other dependencies.

```bash
pip install make_it_real-0.1.0-py3-none-any.whl
make-it-real templates
make-it-real quote examples/tshirt.json
make-it-real quote examples/enclosure.json
```

## Web app and API

Every command is also a JSON API endpoint and a browser form, served by the built-in web app.

```bash
make-it-real-web --port 8000          # then open http://127.0.0.1:8000
make-it-real-web keys create --label "first customer"   # prints an API key (stored hashed)
docker build -t make-it-real . && docker run -p 8000:8000 -e API_KEYS=sk_... -v make-it-real-data:/data make-it-real
```

Every API call needs `Authorization: Bearer <key>` once any key exists; a server on a public address refuses to start without one. Calls are rate-limited per key (60/min, `--rate`) and metered: `make-it-real-web usage` prints calls per key for billing.

Endpoints: `POST /api/templates`, `POST /api/quote`, plus `GET /healthz` and `GET /api/spec` (machine-readable field list).
Files are sent as `{"name": ..., "content": ...}`, folders as `{"files": [...]}` or a base64 zip.

## Deploy and sell

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/eliem08/make-it-real)

`render.yaml` (one click, above) and `fly.toml` (`fly launch --copy-config`) both run the Dockerfile with a persistent `/data` volume and a `/healthz` check.
To sell self-serve, set four variables (full list, names only, in `.env.example`) and point a Stripe webhook at `https://<your-host>/billing/webhook` (events `checkout.session.completed` and `customer.subscription.deleted`):

| Variable | Example |
|---|---|
| `STRIPE_SECRET_KEY` | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` |
| `STRIPE_PRICES` | `creator=price_123,studio=price_456` |
| `PUBLIC_URL` | `https://make-it-real.example.com` |

Buyers pick a plan on `/pricing`, pay on Stripe Checkout and see their API key once on the success page. Cancelling the subscription revokes the key. A selling server always requires a key. Only the monthly plans (Creator, Studio) go through Checkout, each with a 14-day free trial; Fulfilment is contact-sales only and must not be added to `STRIPE_PRICES`.

## Pricing

Every monthly plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Creator** | $15 per month | Unlimited checks and quotes; Print and 3D templates |
| **Studio** | $79 per month | Everything in Creator |
| **Fulfilment** | Custom (per-order margin, contact sales) | We handle manufacturing; Quality checks; Shipping |

All plans unlock the same software in this release — there is no feature gating by plan, and no custom supplier rates or team-seat mechanism exist yet. Studio differs only in licence scope and support, to be confirmed by the owner before selling. Fulfilment is a human service arranged with the owner, not a software feature: this release places no orders with suppliers and has no supplier adapters — the production order is a dict for the buyer to send on.

To start a trial or buy a plan, [request access](https://github.com/eliem08/make-it-real/issues/new?title=Make%20It%20Real%20trial&labels=sales).

## Licence

Proprietary. Copyright (c) 2026 eliem08. All rights reserved. Use requires a paid plan or an active trial; see [LICENSE](LICENSE).
<!-- sell-kit:end -->

## What it does

- **Product templates**: mug, t-shirt, poster, sticker, phone case, enclosure
  — printable area or build envelope, allowed methods, base unit cost
- **Methods** with rules + pricing: sublimation, DTG, screen print, offset,
  vinyl cut, FDM / SLA 3D print, laser cut — setup fee, unit cost, quantity
  breaks, minimum order, lead time
- **Design validation**:
  - artwork effective DPI at print size ≥ 300 (warn ≥ 150)
  - aspect ratio fits the print area
  - colour count limit for screen printing
  - wall thickness / build volume for 3D-printed enclosures
- **Quote**: every valid method priced; cheapest and fastest picked
- **Production order** dict via the Python API (`production_order`), ready to send to a supplier — not a CLI or web output

## Quickstart

```bash
pip install -e .
make-it-real templates
make-it-real quote examples/tshirt.json
make-it-real quote examples/enclosure.json
```

## Roadmap

- Supplier network adapters (print-on-demand APIs, local 3D-print farms)
- Auto-fix: upscale artwork, reduce palette for screen print, thicken walls
- Mockup renders + "order a sample" flow

## Development

Zero runtime dependencies; Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m unittest discover -s tests -t .           # unit + CLI smoke tests
ruff check . && ruff format --check .               # lint + format
python -m pip wheel . --no-deps -w dist            # customer wheel, as in Quickstart
```

```
make_it_real/core.py       domain logic (pure, importable, fully tested)
make_it_real/__main__.py   CLI (`make-it-real ...` / `python -m make_it_real ...`)
tests/                unit tests + generated CLI smoke tests
examples/             sample inputs used by the docs and smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #23).
