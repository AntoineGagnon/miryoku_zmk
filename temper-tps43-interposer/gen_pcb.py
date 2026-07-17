#!/usr/bin/env python3
"""Generate clean Temper TPS43 Interposer PCB.

Uses two 1x12 pin headers (JP1 left, JP2 right), one FFC connector,
and two pull-up resistors.  Nets are pre-assigned to pads; the user
routes traces manually with KiCad's interactive router.
"""

import uuid, os

TAB = "\t"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "temper-tps43-interposer.kicad_pcb")

def U():
    return str(uuid.uuid4())

# ── Geometry ──
PP = 2.54          # pin pitch
RS = 15.24         # row spacing
BW = 34.0          # board width
BH = 44.0          # board height (fits all pins + FFC + resistors)
CY = 1.5           # board Y centre offset (positive = shifted up)
P1Y = 12.7         # Y of pin 1 (topmost)
J1X = -RS / 2      # JP1 X centre
J2X = RS / 2       # JP2 X centre

# ── Library footprint references ──
HEADER_FP = "Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical"
RES_FP    = "Resistor_SMD:R_0805_2012Metric"
FFC_FP    = "temper-tps43-interposer:TPS43_FFC_06"

# ── Net IDs ──
NETS = {"GND": 1, "VCC": 2, "SDA": 3, "SCL": 4, "RDY": 5, "RST": 6}

# ── Pin labels ──
LEFT = {
    1: "D1", 2: "D0", 3: "GND", 4: "GND", 5: "D2", 6: "D3",
    7: "D4", 8: "D5", 9: "D6", 10: "D7", 11: "D8", 12: "D9",
}
RIGHT = {
    1: "RAW", 2: "GND", 3: "RST", 4: "VCC", 5: "D21", 6: "D20",
    7: "D19", 8: "D18", 9: "D15", 10: "D14", 11: "D16", 12: "D10",
}

def pin_net(label):
    if label == "VCC": return NETS["VCC"]
    if label == "GND": return NETS["GND"]
    m = {"D8": NETS["SDA"], "D9": NETS["SCL"],
         "D10": NETS["RDY"], "D16": NETS["RST"]}
    return m.get(label, 0)

# ── Build ──
lines = []
A = lines.append

# ----- header (KiCad 9 format) -----
A("(kicad_pcb")
A(TAB + '(version 20241229)')
A(TAB + '(generator "pcbnew")')
A(TAB + '(generator_version "9.0")')
A(TAB + "(general")
A(TAB + TAB + "(thickness 1.0)")
A(TAB + TAB + "(legacy_teardrops no)")
A(TAB + ")")
A(TAB + '(paper "A4")')

# layers
A(TAB + "(layers")
for s in [
    TAB + TAB + '(0 "F.Cu" signal)',          TAB + TAB + '(2 "B.Cu" signal)',
    TAB + TAB + '(9 "F.Adhes" user "F.Adhesive")',
    TAB + TAB + '(11 "B.Adhes" user "B.Adhesive")',
    TAB + TAB + '(13 "F.Paste" user)',        TAB + TAB + '(15 "B.Paste" user)',
    TAB + TAB + '(5 "F.SilkS" user "F.Silkscreen")',
    TAB + TAB + '(7 "B.SilkS" user "B.Silkscreen")',
    TAB + TAB + '(1 "F.Mask" user)',          TAB + TAB + '(3 "B.Mask" user)',
    TAB + TAB + '(17 "Dwgs.User" user "User.Drawings")',
    TAB + TAB + '(19 "Cmts.User" user "User.Comments")',
    TAB + TAB + '(21 "Eco1.User" user "User.Eco1")',
    TAB + TAB + '(23 "Eco2.User" user "User.Eco2")',
    TAB + TAB + '(25 "Edge.Cuts" user)',      TAB + TAB + '(27 "Margin" user)',
    TAB + TAB + '(31 "F.CrtYd" user "F.Courtyard")',
    TAB + TAB + '(29 "B.CrtYd" user "B.Courtyard")',
    TAB + TAB + '(35 "F.Fab" user)',          TAB + TAB + '(33 "B.Fab" user)',
    TAB + TAB + '(39 "User.1" user)',         TAB + TAB + '(41 "User.2" user)',
    TAB + TAB + '(43 "User.3" user)',         TAB + TAB + '(45 "User.4" user)',
]:
    A(s)
A(TAB + ")")

# setup
for s in [
    TAB + "(setup",
    TAB + TAB + "(pad_to_mask_clearance 0)",
    TAB + TAB + "(allow_soldermask_bridges_in_footprints no)",
    TAB + TAB + "(tenting front back)",
    TAB + TAB + "(pcbplotparams",
    TAB + TAB + TAB + "(layerselection 0x00000000_00000000_55555555_5755f5ff)",
    TAB + TAB + TAB + "(plot_on_all_layers_selection 0x00000000_00000000_00000000_00000000)",
    TAB + TAB + TAB + "(disableapertmacros no)",
    TAB + TAB + TAB + "(usegerberextensions no)",
    TAB + TAB + TAB + "(usegerberattributes yes)",
    TAB + TAB + TAB + "(usegerberadvancedattributes yes)",
    TAB + TAB + TAB + "(creategerberjobfile yes)",
    TAB + TAB + TAB + "(dashed_line_dash_ratio 12.000000)",
    TAB + TAB + TAB + "(dashed_line_gap_ratio 3.000000)",
    TAB + TAB + TAB + "(svgprecision 4)",
    TAB + TAB + TAB + "(plotframeref no)",
    TAB + TAB + TAB + "(mode 1)",
    TAB + TAB + TAB + "(useauxorigin no)",
    TAB + TAB + TAB + "(hpglpennumber 1)",
    TAB + TAB + TAB + "(hpglpenspeed 20)",
    TAB + TAB + TAB + "(hpglpendiameter 15.000000)",
    TAB + TAB + TAB + "(pdf_front_fp_property_popups yes)",
    TAB + TAB + TAB + "(pdf_back_fp_property_popups yes)",
    TAB + TAB + TAB + "(pdf_metadata yes)",
    TAB + TAB + TAB + "(pdf_single_document no)",
    TAB + TAB + TAB + "(dxfpolygonmode yes)",
    TAB + TAB + TAB + "(dxfimperialunits yes)",
    TAB + TAB + TAB + "(dxfusepcbnewfont yes)",
    TAB + TAB + TAB + "(psnegative no)",
    TAB + TAB + TAB + "(psa4output no)",
    TAB + TAB + TAB + "(plot_black_and_white yes)",
    TAB + TAB + TAB + "(sketchpadsonfab no)",
    TAB + TAB + TAB + "(plotpadnumbers no)",
    TAB + TAB + TAB + "(hidednponfab no)",
    TAB + TAB + TAB + "(sketchdnponfab yes)",
    TAB + TAB + TAB + "(crossoutdnponfab yes)",
    TAB + TAB + TAB + "(subtractmaskfromsilk no)",
    TAB + TAB + TAB + "(outputformat 1)",
    TAB + TAB + TAB + "(mirror no)",
    TAB + TAB + TAB + "(drillshape 1)",
    TAB + TAB + TAB + "(scaleselection 1)",
    TAB + TAB + TAB + '(outputdirectory "")',
    TAB + TAB + ")",
    TAB + ")",
]:
    A(s)

# nets
for name, nid in NETS.items():
    A(TAB + f'(net {nid} "{name}")')
A(TAB + '(net 0 "")')

# ── Helpers ──────────────────────────────────────────────────────────
def prop(name, value, x, y, layer, hide=False):
    A(TAB + TAB + f'(property "{name}" "{value}"')
    A(TAB + TAB + TAB + f"(at {x:.2f} {y:.2f} 0)")
    A(TAB + TAB + TAB + f'(layer "{layer}")')
    if hide:
        A(TAB + TAB + TAB + "(hide yes)")
    A(TAB + TAB + TAB + f'(uuid "{U()}")')
    A(TAB + TAB + TAB + "(effects (font (size 1 1) (thickness 0.15)))")
    A(TAB + TAB + ")")

def pad_net(pnum, net_id):
    """Set net on an existing library pad — no geometry override."""
    if net_id > 0:
        nm = {v: k for k, v in NETS.items()}.get(net_id, "")
        A(TAB + TAB + TAB + f'(pad "{pnum}" (net {net_id} "{nm}"))')
    else:
        A(TAB + TAB + TAB + f'(pad "{pnum}" (net 0 ""))')

def footprint_start(libid, fp_uuid, x, y, rot, descr, tags, attr):
    A(TAB + f'(footprint "{libid}"')
    A(TAB + TAB + f'(layer "F.Cu")')
    A(TAB + TAB + f'(uuid "{fp_uuid}")')
    A(TAB + TAB + f"(at {x:.2f} {y:.2f} {rot})")
    if descr: A(TAB + TAB + f'(descr "{descr}")')
    if tags:  A(TAB + TAB + f'(tags "{tags}")')
    if attr:  A(TAB + TAB + f"(attr {attr})")

def footprint_end():
    A(TAB + ")")

# ── JP1 (left row, 12 pins) ──
footprint_start(HEADER_FP, U(), J1X, P1Y - 5.5 * PP, 0,
                "Left Pro Micro header", "pin header", "exclude_from_pos_files exclude_from_bom")
prop("Reference", "JP1", J1X - 3.5, P1Y - 5.5 * PP, "F.SilkS")
prop("Value", "ProMicro Left", J1X - 3.5, P1Y - 5.5 * PP - 2, "F.Fab", hide=True)
for pn in range(1, 13):
    y = (pn - 1) * -PP  # relative to FP centre (pin 1 at top)
    label = LEFT[pn]
    net_id = pin_net(label)
    pad_net(str(pn), net_id)
footprint_end()

# ── JP2 (right row, 12 pins) ──
footprint_start(HEADER_FP, U(), J2X, P1Y - 5.5 * PP, 0,
                "Right Pro Micro header", "pin header", "exclude_from_pos_files exclude_from_bom")
prop("Reference", "JP2", J2X + 2, P1Y - 5.5 * PP, "F.SilkS")
prop("Value", "ProMicro Right", J2X + 2, P1Y - 5.5 * PP - 2, "F.Fab", hide=True)
for pn in range(1, 13):
    y = (pn - 1) * -PP
    label = RIGHT[pn]
    net_id = pin_net(label)
    pad_net(str(pn), net_id)
footprint_end()

# ── FFC connector ──
ffc_y = P1Y + 3.0
footprint_start(FFC_FP, U(), 0, ffc_y, 0,
                "6-pin 0.5mm FFC for TPS43", "FFC FPC", "smd")
prop("Reference", "CON1", 0, ffc_y + 2, "F.SilkS")
prop("Value", "TPS43 FFC", 0, ffc_y + 3.5, "F.Fab", hide=True)
ffc_map = [(1, NETS["VCC"]), (2, NETS["SDA"]), (3, NETS["SCL"]),
           (4, NETS["RDY"]), (5, NETS["RST"]), (6, NETS["GND"])]
for pi, nid in ffc_map:
    pad_net(str(pi), nid)
footprint_end()

# ── Resistors ──
r1_y = ffc_y + 5.0
r2_y = ffc_y + 2.5
rrx = J1X + 4.0
for rname, ry, src_net in [("R1", r1_y, NETS["SDA"]), ("R2", r2_y, NETS["SCL"])]:
    footprint_start(RES_FP, U(), rrx, ry, 90,
                    "2.2kΩ pull-up", "resistor", "smd")
    prop("Reference", rname, rrx, ry + 2, "F.SilkS")
    prop("Value", "2.2k", rrx, ry - 2, "F.Fab")
    pad_net("1", src_net)
    pad_net("2", NETS["VCC"])
    footprint_end()

# ── Board outline ──
hw = BW / 2; hh = BH / 2
ol = [(-hw, CY + hh), (hw, CY + hh), (hw, CY - hh), (-hw, CY - hh)]
for i in range(4):
    x1, y1 = ol[i]; x2, y2 = ol[(i + 1) % 4]
    A(TAB + f"(gr_line (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f})"
      f' (layer "Edge.Cuts") (width 0.1) (uuid "{U()}"))')

# ── Silkscreen ──
for tx, sx, sy, fs in [
    ("Temper TPS43 Interposer",  0,       CY + hh - 1.5, "1.0 1.0"),
    ("v1.0",                     0,       CY + hh - 2.8, "0.8 0.8"),
    ("SDA  SCL  RDY  RST",       0,       ffc_y - 2.5,   "0.8 0.8"),
    ("VCC                    GND", 0,     ffc_y - 4.0,   "0.6 0.6"),
    ("Top: nice!nano   Bottom: Temper", 0, CY - hh + 2,  "0.9 0.9"),
]:
    A(TAB + f'(gr_text "{tx}" (at {sx:.2f} {sy:.2f} 0) (layer "F.SilkS")'
      f" (effects (font (size {fs}) (thickness 0.15))) (uuid \"{U()}\"))")

# Tap labels near relevant pins
tap_labels = [
    ("D8",  J1X - 2.5, P1Y - 10 * PP),
    ("D9",  J1X - 2.5, P1Y - 11 * PP),
    ("D10", J2X + 2.5, P1Y - 11 * PP),
    ("D16", J2X + 2.5, P1Y - 10 * PP),
    ("VCC", J2X + 2.5, P1Y -  3 * PP),
    ("GND", J1X - 2.5, P1Y -  2 * PP),
]
for lb, tx, ty in tap_labels:
    A(TAB + f'(gr_text "{lb}" (at {tx:.2f} {ty:.2f} 0) (layer "F.SilkS")'
      f" (effects (font (size 0.6 0.6) (thickness 0.075))) (uuid \"{U()}\"))")

A(TAB + "(embedded_fonts no)")
A(")")

# ── Write ──
if __name__ == "__main__":
    content = "\n".join(lines) + "\n"
    with open(OUT, "w") as f:
        f.write(content)
    print(f"Generated {OUT} ({len(content)} bytes)")
    print(f"Headers:  JP1 (left, 12 pins), JP2 (right, 12 pins)")
    print(f"FFC:     CON1 ({ffc_y:.1f} mm from centre)")
    print(f"Resistors: R1 (SDA→VCC), R2 (SCL→VCC)")
    print(f"Board:   {BW:.0f}×{BH:.0f} mm")
    print(f"  → Run KiCad interactive router to connect tapped pins to FFC & resistors.")
