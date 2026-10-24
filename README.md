# make-it-real

[![CI](https://github.com/eliem08/make-it-real/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/make-it-real/actions/workflows/ci.yml)

> **Canva for physical products** — design it with AI and get it made.

Image models can design a mug, a hoodie or a little electronics enclosure in
seconds. Turning that into something a factory will actually make is where
people get stuck: DPI, print areas, colour limits, wall thickness, minimums.
`make-it-real` is the manufacturability + quoting engine that sits between
the AI design and the print shop / 3D-print farm.

## What the MVP does

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
