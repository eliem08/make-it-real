import argparse
import json
import sys

from .core import METHODS, TEMPLATES, quote


def main(argv=None):
    ap = argparse.ArgumentParser(prog="make-it-real")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("templates")
    q = sub.add_parser("quote")
    q.add_argument("design")
    a = ap.parse_args(argv)
    if a.cmd == "templates":
        for t in TEMPLATES.values():
            area = f'{t.print_in[0]}x{t.print_in[1]} in' if t.print_in else "3D part"
            print(f"{t.key:<12} {area:<14} methods: {', '.join(t.methods)}")
        return 0
    with open(a.design, encoding="utf-8") as fh:
        res = quote(json.load(fh))
    print(f"{res['template']} x {res['quantity']}")
    for o in res["options"]:
        status = "OK " if o["valid"] else "NO "
        print(f"  {status}{o['method']:<15} ${o['total']:>9,.2f}  (${o['unit']:.2f}/unit + ${o['setup']:.0f} setup, {o['lead_days']}d)")
        for e in o["errors"]:
            print(f"       x {e}")
        for w in o["warnings"]:
            print(f"       ! {w}")
    print(f"cheapest: {res['cheapest']}   fastest: {res['fastest']}")
    return 0 if res["cheapest"] else 1


if __name__ == "__main__":
    sys.exit(main())
