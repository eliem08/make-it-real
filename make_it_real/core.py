"""Manufacturability checks and quoting for AI-designed physical products."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Template", "Method", "TEMPLATES", "METHODS", "validate", "quote", "production_order"]


@dataclass(frozen=True)
class Method:
    key: str
    setup: float
    unit: float
    breaks: tuple = ()  # ((qty, multiplier), ...)
    min_qty: int = 1
    lead_days: int = 5
    max_colors: int | None = None
    min_wall_mm: float | None = None
    build_mm: tuple | None = None

    def unit_price(self, qty: int) -> float:
        mult = 1.0
        for q, m in self.breaks:
            if qty >= q:
                mult = m
        return self.unit * mult


@dataclass(frozen=True)
class Template:
    key: str
    kind: str  # "print" or "3d"
    print_in: tuple = ()  # printable area in inches (w, h)
    base_cost: float = 0.0
    methods: tuple = ()


METHODS = {
    "sublimation": Method("sublimation", 0, 4.0, ((50, 0.85), (250, 0.7)), lead_days=4),
    "dtg": Method("dtg", 0, 7.5, ((50, 0.9), (250, 0.8)), lead_days=5),
    "screen_print": Method("screen_print", 25, 1.8, ((100, 0.75), (500, 0.55)), min_qty=24, lead_days=10, max_colors=6),
    "offset": Method("offset", 150, 0.6, ((500, 0.6), (2000, 0.4)), min_qty=250, lead_days=12),
    "digital_print": Method("digital_print", 0, 3.0, ((50, 0.8),), lead_days=3),
    "vinyl_cut": Method("vinyl_cut", 10, 0.9, ((100, 0.6),), min_qty=10, lead_days=4, max_colors=2),
    "fdm": Method("fdm", 0, 0.08, ((20, 0.9), (100, 0.75)), lead_days=4, min_wall_mm=1.2, build_mm=(250, 210, 210)),
    "sla": Method("sla", 0, 0.22, ((20, 0.9), (100, 0.8)), lead_days=6, min_wall_mm=0.8, build_mm=(145, 145, 175)),
    "injection_mold": Method(
        "injection_mold",
        6000,
        0.002,
        ((5000, 0.7),),
        min_qty=1000,
        lead_days=35,
        min_wall_mm=1.0,
        build_mm=(400, 400, 300),
    ),
}

TEMPLATES = {
    "mug": Template("mug", "print", (8.5, 3.5), 3.2, ("sublimation",)),
    "tshirt": Template("tshirt", "print", (12, 16), 4.5, ("dtg", "screen_print")),
    "poster": Template("poster", "print", (18, 24), 1.5, ("digital_print", "offset")),
    "sticker": Template("sticker", "print", (3, 3), 0.1, ("digital_print", "vinyl_cut")),
    "phone_case": Template("phone_case", "print", (2.8, 5.8), 3.0, ("sublimation", "digital_print")),
    "enclosure": Template("enclosure", "3d", (), 0.0, ("fdm", "sla", "injection_mold")),
}


def _print_issues(t: Template, m: Method, art: dict) -> tuple[list, list]:
    errors, warnings = [], []
    w_in, h_in = t.print_in
    w_px, h_px = art["width_px"], art["height_px"]
    scale = min(w_in / w_px, h_in / h_px)  # inches per pixel when fit to area
    dpi = 1 / scale
    if dpi < 150:
        errors.append(f"artwork only {dpi:.0f} DPI at print size (need 300)")
    elif dpi < 300:
        warnings.append(f"artwork {dpi:.0f} DPI at print size; 300 recommended")
    art_ratio, area_ratio = w_px / h_px, w_in / h_in
    if abs(art_ratio - area_ratio) / area_ratio > 0.25:
        warnings.append(f"aspect ratio {art_ratio:.2f} vs print area {area_ratio:.2f} - design will be letterboxed")
    if m.max_colors and art.get("colors", 99) > m.max_colors:
        errors.append(f"{art.get('colors')} colours exceeds {m.key} limit of {m.max_colors}")
    return errors, warnings


def _3d_issues(m: Method, model: dict) -> tuple[list, list]:
    errors, warnings = [], []
    dims = sorted((model["x_mm"], model["y_mm"], model["z_mm"]))
    if m.build_mm and any(d > b for d, b in zip(dims, sorted(m.build_mm))):
        errors.append(f"part {dims} mm exceeds {m.key} build volume {m.build_mm}")
    if m.min_wall_mm and model["wall_mm"] < m.min_wall_mm:
        errors.append(f"wall {model['wall_mm']} mm below {m.key} minimum {m.min_wall_mm} mm")
    return errors, warnings


def validate(design: dict, method_key: str) -> tuple[list, list]:
    t = TEMPLATES[design["template"]]
    m = METHODS[method_key]
    errors, warnings = _print_issues(t, m, design["artwork"]) if t.kind == "print" else _3d_issues(m, design["model"])
    if design["quantity"] < m.min_qty:
        errors.append(f"{m.key} minimum order is {m.min_qty}")
    return errors, warnings


def _shell_cm3(model):
    x, y, z, w = (model[k] / 10 for k in ("x_mm", "y_mm", "z_mm", "wall_mm"))
    return x * y * z - max(0, x - 2 * w) * max(0, y - 2 * w) * max(0, z - 2 * w)


def quote(design: dict) -> dict:
    if not isinstance(design, dict):
        raise ValueError("design must be a JSON object")
    t = TEMPLATES[design["template"]]
    qty = design["quantity"]
    options = []
    for key in t.methods:
        m = METHODS[key]
        errors, warnings = validate(design, key)
        if t.kind == "3d":
            unit = m.unit_price(qty) * _shell_cm3(design["model"])
            unit = max(unit, 0.5)
        else:
            unit = t.base_cost + m.unit_price(qty)
        total = round(m.setup + unit * qty, 2)
        options.append(
            {
                "method": key,
                "valid": not errors,
                "errors": errors,
                "warnings": warnings,
                "unit": round(unit, 2),
                "setup": m.setup,
                "total": total,
                "lead_days": m.lead_days,
            }
        )
    valid = [o for o in options if o["valid"]]
    return {
        "template": t.key,
        "quantity": qty,
        "options": options,
        "cheapest": min(valid, key=lambda o: o["total"])["method"] if valid else None,
        "fastest": min(valid, key=lambda o: (o["lead_days"], o["total"]))["method"] if valid else None,
    }


def production_order(design: dict, method_key: str, ship_to: str = "") -> dict:
    errors, _ = validate(design, method_key)
    if errors:
        raise ValueError("; ".join(errors))
    q = next(o for o in quote(design)["options"] if o["method"] == method_key)
    return {
        "product": design["template"],
        "method": method_key,
        "quantity": design["quantity"],
        "unit_price": q["unit"],
        "setup": q["setup"],
        "total": q["total"],
        "lead_days": q["lead_days"],
        "spec": design.get("artwork") or design.get("model"),
        "ship_to": ship_to,
    }
