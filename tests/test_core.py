import unittest

from make_it_real import production_order, quote, validate

SHIRT = {"template": "tshirt", "quantity": 60, "artwork": {"width_px": 3600, "height_px": 4800, "colors": 3}}


class Tests(unittest.TestCase):
    def test_shirt_methods(self):
        q = quote(SHIRT)
        self.assertEqual({o["method"] for o in q["options"] if o["valid"]}, {"dtg", "screen_print"})
        self.assertEqual(q["cheapest"], "screen_print")
        self.assertEqual(q["fastest"], "dtg")

    def test_low_dpi_and_colours(self):
        bad = {**SHIRT, "artwork": {"width_px": 1000, "height_px": 1300, "colors": 9}}
        errors, _ = validate(bad, "screen_print")
        self.assertTrue(any("DPI" in e for e in errors))
        self.assertTrue(any("colours" in e for e in errors))

    def test_min_qty(self):
        errors, _ = validate({**SHIRT, "quantity": 5}, "screen_print")
        self.assertIn("screen_print minimum order is 24", errors)

    def test_enclosure(self):
        box = {"template": "enclosure", "quantity": 25, "model": {"x_mm": 200, "y_mm": 60, "z_mm": 30, "wall_mm": 1.0}}
        q = quote(box)
        valid = {o["method"]: o for o in q["options"]}
        self.assertFalse(valid["fdm"]["valid"])  # wall too thin
        self.assertFalse(valid["sla"]["valid"])  # too big
        self.assertFalse(valid["injection_mold"]["valid"])  # min qty
        self.assertIsNone(q["cheapest"])
        box["model"].update(x_mm=90, wall_mm=1.6)
        self.assertEqual(quote(box)["cheapest"], "fdm")

    def test_production_order(self):
        order = production_order(SHIRT, "dtg", "Acme, 1 Main St")
        self.assertEqual(order["quantity"], 60)
        with self.assertRaises(ValueError):
            production_order({**SHIRT, "quantity": 5}, "screen_print")

    def test_impossible_parts_and_quantities_never_quote_as_valid(self):
        base = {"template": "enclosure", "quantity": 25, "model": {"x_mm": 90, "y_mm": 60, "z_mm": 30, "wall_mm": 1.6}}
        bad_designs = [
            {**base, "model": {**base["model"], "x_mm": -90}},
            {**base, "model": {**base["model"], "wall_mm": float("nan")}},
            {**base, "quantity": 2.5},
            {**base, "quantity": 0},
        ]
        for design in bad_designs:
            with self.subTest(design=design):
                q = quote(design)
                self.assertIsNone(q["cheapest"])
                self.assertFalse(any(o["valid"] for o in q["options"]))


if __name__ == "__main__":
    unittest.main()
