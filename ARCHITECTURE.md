# Architecture — make-it-real

## 1. Scope
Turn AI-generated designs into manufacturable, priced orders.
**MVP:** product templates (print area / 3D), manufacturing methods with constraints and quantity
breaks, validators (DPI, aspect, colour count, wall thickness, build volume, MOQ), multi-method
quote with cheapest and fastest, production order.
**Product:** supplier network adapters, auto-fix (upscale, palette reduction, wall thickening), mockups, sampling.

## 2. System context
```mermaid
flowchart LR
  Designer[AI design tool] -->|artwork / 3D model + specs| Validate
  Templates[(Templates & methods)] --> Validate
  Validate --> Quote[Quote all valid methods]
  Quote --> Customer
  Customer -->|order| Router[Supplier router]
  Router --> POD[Print-on-demand APIs] & Farm[3D print farms] & Factory[Injection moulders]
```

## 3. Validation rules
- **Print:** effective DPI = `px / inches` when fitted to the print area. Under 150 is an error,
  under 300 a warning. Aspect mismatch over 25% is a warning. Screen-print colour limits apply.
- **3D:** the part fits the build volume in *any orientation* (sorted dimensions are compared),
  and walls meet the method's minimum thickness.
- **Any method:** minimum order quantity.

## 4. Pricing
- **Print:** `template_base + method_unit × break(qty)`, plus setup.
- **3D:** `shell_volume_cm³ × method_rate × break(qty)` (hollow-shell approximation), plus setup,
  with a floor per unit.

## 5. Design decisions
- **Templates and methods as data.** Adding a product is configuration, not code.
- **Quote every method** and let the customer trade price against lead time. Cheapest and fastest are highlighted.
- **Orientation-agnostic fit check.** It avoids false rejections. *Trade-off:* it ignores support
  material and overhangs. Slicer integration is on the roadmap.

## 6. Production architecture
A quote service (stateless), a supplier adapter layer (Printful/Printify APIs, Craftcloud-style
3D networks, RFQ email for moulders), an order state machine (`quoted → paid → in_production →
shipped`), and file storage for print-ready assets (PDF/X, STL/STEP).

## 7. Risks
IP infringement in AI artwork, so trademark and logo screening is needed before production.
Supplier quality variance is handled with sample-first orders and supplier scorecards.
