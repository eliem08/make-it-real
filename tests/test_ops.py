import contextlib
import io
import os
import tempfile
import unittest

from make_it_real.__main__ import main
from make_it_real.ops import load

EX = os.path.join(os.path.dirname(__file__), "..", "examples")
TSHIRT = os.path.join(EX, "tshirt.json")


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class OrderOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "orders.json")
        self.s = ["--store", self.path]

    def tearDown(self):
        self.tmp.cleanup()

    def ok(self, *argv):
        code, out = run(*argv, *self.s)
        self.assertEqual(code, 0, out)
        return out

    def test_order_freezes_the_price_and_follows_the_production_flow(self):
        self.assertIn("PO-00001", self.ok("order-place", "Ana", TSHIRT, "--ship-to", "1 Main St, Lyon"))
        order = load(self.path)["orders"]["PO-00001"]
        self.assertEqual((order["status"], order["ship_to"]), ("placed", "1 Main St, Lyon"))
        self.assertGreater(order["total"], 0)
        self.assertEqual(run("order-update", "PO-00001", "shipped", "--tracking", "T1", *self.s)[0], 1)  # skips a step
        self.ok("order-update", "PO-00001", "in_production")
        self.assertEqual(run("order-update", "PO-00001", "shipped", *self.s)[0], 1)  # no tracking
        self.assertIn("tracking 1Z999", self.ok("order-update", "PO-00001", "shipped", "--tracking", "1Z999"))
        self.ok("order-update", "PO-00001", "delivered")
        self.assertEqual(run("order-update", "PO-00001", "cancelled", *self.s)[0], 1)  # final
        self.assertIn("delivered", self.ok("orders"))

    def test_unmakeable_designs_and_bad_requests_are_refused(self):
        bad = os.path.join(self.tmp.name, "bad.json")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write('{"template": "tshirt", "quantity": 1, "artwork": {"width_px": 10, "height_px": 10, "colors": 2}}')
        for argv in (
            ["order-place", "Ana", bad, "--ship-to", "x"],  # 1 DPI artwork
            ["order-place", "Ana", TSHIRT, "--ship-to", " "],
            ["order-place", "Ana", TSHIRT, "--ship-to", "x", "--method", "injection_mold"],  # not for t-shirts
            ["order-show", "PO-99999"],
        ):
            with self.subTest(argv=argv[:3]):
                self.assertEqual(run(*argv, *self.s)[0], 1)
        self.assertEqual(load(self.path)["orders"], {})


if __name__ == "__main__":
    unittest.main()
