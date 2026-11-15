"""Operating commands: turn a validated design into a tracked production order (also served by the web app).

An order freezes the price, method and spec at the moment it is placed. Sending the job to a manufacturer
and charging the customer happen outside this tool; `order-update` records where the job is.
"""

import itertools
import json
import os
import time

from .core import METHODS, production_order, quote

OPS = ("order-place", "order-update", "order-show", "orders")
FLOW = {
    "placed": ("in_production", "cancelled"),
    "in_production": ("shipped", "cancelled"),
    "shipped": ("delivered",),
    "delivered": (),
    "cancelled": (),
}


class OrderError(ValueError):
    pass


def load(path: str) -> dict:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except FileNotFoundError:
        return {"orders": {}, "next_id": 1}
    if not isinstance(doc, dict) or not isinstance(doc.get("orders"), dict):
        raise OrderError(f"{path}: not a make-it-real store")
    return doc


def save(doc: dict, path: str):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
    os.replace(tmp, path)


def add_ops(sub):
    store = os.environ.get("MAKE_IT_REAL_STORE", "orders.json")
    p = sub.add_parser("order-place", help="place a production order for a design that passes its checks")
    p.add_argument("customer")
    p.add_argument("design", help="the design JSON file")
    p.add_argument("--method", choices=sorted(METHODS), help="default: the cheapest valid method")
    p.add_argument("--ship-to", required=True)
    p = sub.add_parser("order-update", help="move an order forward")
    p.add_argument("order_id")
    p.add_argument("status", choices=sorted({s for nxt in FLOW.values() for s in nxt}))
    p.add_argument("--tracking", default="", help="carrier tracking reference, when shipped")
    sub.add_parser("order-show", help="one order in full").add_argument("order_id")
    sub.add_parser("orders", help="every order and where it is")
    for name in OPS:
        sub.choices[name].add_argument("--store", default=store)


def run_ops(a) -> int:
    try:
        doc = load(a.store)
        _run(doc, a)
        save(doc, a.store)
        return 0
    except (ValueError, KeyError) as e:
        print(f"refused: {e.args[0] if e.args else e}")
        return 1


def _order(doc: dict, oid: str) -> dict:
    if oid not in doc["orders"]:
        raise OrderError(f"no order {oid!r}")
    return doc["orders"][oid]


def _run(doc: dict, a):
    c = a.cmd
    if c == "order-place":
        with open(a.design, encoding="utf-8-sig") as fh:
            design = json.load(fh)
        method = a.method or quote(design)["cheapest"]
        if not method:
            raise OrderError("no manufacturing method can make this design as specified; run quote to see why")
        if not a.ship_to.strip():
            raise OrderError("a shipping address is required")
        po = production_order(design, method, a.ship_to.strip())
        ids = itertools.count(int(doc.get("next_id", 1)))
        oid = f"PO-{next(ids):05d}"
        doc["next_id"] = next(ids)
        doc["orders"][oid] = {
            **po,
            "customer": a.customer,
            "status": "placed",
            "tracking": "",
            "placed": int(time.time()),
        }
        print(f"{oid}: {po['quantity']} x {po['product']} by {method} for {a.customer}")
        print(
            f"  ${po['total']:,.2f} (${po['unit_price']:.2f}/unit + ${po['setup']:.0f} setup), about {po['lead_days']} days"
        )
    elif c == "order-update":
        o = _order(doc, a.order_id)
        if a.status not in FLOW[o["status"]]:
            allowed = ", ".join(FLOW[o["status"]]) or "nothing: it is final"
            raise OrderError(f"{a.order_id} is {o['status']}; it can only move to {allowed}")
        if a.status == "shipped" and not a.tracking.strip():
            raise OrderError("--tracking is required when an order ships")
        o["status"] = a.status
        if a.tracking.strip():
            o["tracking"] = a.tracking.strip()
        print(f"{a.order_id} is now {a.status}" + (f" (tracking {o['tracking']})" if o["tracking"] else ""))
    elif c == "order-show":
        print(json.dumps(_order(doc, a.order_id), indent=2))
    else:
        for oid, o in doc["orders"].items():
            print(
                f"{oid}  {o['status']:<14}{o['customer']:<18}{o['quantity']:>5} x {o['product']:<11}${o['total']:>10,.2f}"
            )
        if not doc["orders"]:
            print("no orders yet")
