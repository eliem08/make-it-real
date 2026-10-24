# make-it-real

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
