import argparse
import csv
import json
import os
import sys

from .core import TEMPLATES, quote


def build_parser():
    ap = argparse.ArgumentParser(prog="make-it-real")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("templates")
    q = sub.add_parser("quote")
    q.add_argument("design")
    return ap


def _run(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.cmd == "templates":
        for t in TEMPLATES.values():
            area = f"{t.print_in[0]}x{t.print_in[1]} in" if t.print_in else "3D part"
            print(f"{t.key:<12} {area:<14} methods: {', '.join(t.methods)}")
        return 0
    with open(a.design, encoding="utf-8-sig") as fh:
        res = quote(json.load(fh))
    print(f"{res['template']} x {res['quantity']}")
    for o in res["options"]:
        status = "OK " if o["valid"] else "NO "
        print(
            f"  {status}{o['method']:<15} ${o['total']:>9,.2f}  (${o['unit']:.2f}/unit + ${o['setup']:.0f} setup, {o['lead_days']}d)"
        )
        for e in o["errors"]:
            print(f"       x {e}")
        for w in o["warnings"]:
            print(f"       ! {w}")
    print(f"cheapest: {res['cheapest']}   fastest: {res['fastest']}")
    return 0 if res["cheapest"] else 1


def main(argv=None):
    """Run the CLI; a bad input file or argument exits 2 with a one-line error instead of a traceback.

    Set AGENT_ECONOMY_DEBUG=1 to see the full traceback.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    try:
        return _run(argv)
    except (OSError, ValueError, KeyError, csv.Error) as e:
        if os.environ.get("AGENT_ECONOMY_DEBUG"):
            raise
        msg = e.args[0] if isinstance(e, KeyError) and e.args else e
        print(f"error: {msg}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
