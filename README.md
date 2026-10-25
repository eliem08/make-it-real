<!-- sell-kit:start -->
# Make It Real

[![CI](https://github.com/eliem08/make-it-real/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/make-it-real/actions/workflows/ci.yml)

> **Design a physical product with AI and get it made.**

**Who it's for:** Creators and small brands turning AI designs into merch, prints and 3D-printed parts.

**The problem:** AI designs look great on screen but fail at the factory: wrong DPI, too many colours, walls too thin, minimums too high.

**What you get:** Manufacturability checks and side-by-side quotes across print and 3D methods, then a production order for the cheapest valid option.

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

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Creator** | $15 per month | Unlimited checks and quotes; Print and 3D templates |
| **Studio** | $79 per month | Production orders; Custom supplier rates; Team seats |
| **Fulfilment** | Custom (per-order margin, contact sales) | We handle manufacturing; Quality checks; Shipping |

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
- **Production order** JSON ready to send to a supplier

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
