#!/usr/bin/env python3
"""Generate clean Temper TPS43 Interposer PCB with proper library footprints."""

import uuid, os

TAB = "\t"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "temper-tps43-interposer.kicad_pcb")

def U():
    return str(uuid.uuid4())

# ── Geometry ───────────────────────────────────────────────────────────
PP = 2.54
RS = 15.24
P1Y = 12.7
J1X = -RS / 2
J2X = RS / 2
BW = 34.0
BH = 20.0

LEFT = {
    1: "D1", 2: "D0", 3: "GND", 4: "GND", 5: "D2", 6: "D3",
    7: "D4", 8: "D5", 9: "D6", 10: "D7", 11: "D8", 12: "D9",
}
RIGHT = {
    1: "RAW", 2: "GND", 3: "RST", 4: "VCC", 5: "D21", 6: "D20",
    7: "D19", 8: "D18", 9: "D15", 10: "D14", 11: "D16", 12: "D10",
}

def pnet(label):
    if label == "VCC":
        return 2
    if label == "GND":
        return 1
    m = {"D8": 3, "D9": 4, "D10": 5, "D16": 6}
    return m.get(label, 0)

# Library references
PIN_FP = "Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical"
RES_FP = "Resistor_SMD:R_0805_2012Metric"
FFC_FP = "temper-tps43-interposer:TPS43_FFC_06"

# ── Build ──────────────────────────────────────────────────────────────
lines = []
A = lines.append

# Header (exact KiCAD 9 format)
A("(kicad_pcb")
A(TAB + '(version 20241229)')
A(TAB + '(generator "pcbnew")')
A(TAB + '(generator_version "9.0")')
A(TAB + "(general")
A(TAB + TAB + "(thickness 1.0)")
A(TAB + TAB + "(legacy_teardrops no)")
A(TAB + ")")
A(TAB + '(paper "A4")')

A(TAB + "(layers")
for s in [
    TAB + TAB + '(0 "F.Cu" signal)',
    TAB + TAB + '(2 "B.Cu" signal)',
    TAB + TAB + '(9 "F.Adhes" user "F.Adhesive")',
    TAB + TAB + '(11 "B.Adhes" user "B.Adhesive")',
    TAB + TAB + '(13 "F.Paste" user)',
    TAB + TAB + '(15 "B.Paste" user)',
    TAB + TAB + '(5 "F.SilkS" user "F.Silkscreen")',
    TAB + TAB + '(7 "B.SilkS" user "B.Silkscreen")',
    TAB + TAB + '(1 "F.Mask" user)',
    TAB + TAB + '(3 "B.Mask" user)',
    TAB + TAB + '(17 "Dwgs.User" user "User.Drawings")',
    TAB + TAB + '(19 "Cmts.User" user "User.Comments")',
    TAB + TAB + '(21 "Eco1.User" user "User.Eco1")',
    TAB + TAB + '(23 "Eco2.User" user "User.Eco2")',
    TAB + TAB + '(25 "Edge.Cuts" user)',
    TAB + TAB + '(27 "Margin" user)',
    TAB + TAB + '(31 "F.CrtYd" user "F.Courtyard")',
    TAB + TAB + '(29 "B.CrtYd" user "B.Courtyard")',
    TAB + TAB + '(35 "F.Fab" user)',
    TAB + TAB + '(33 "B.Fab" user)',
    TAB + TAB + '(39 "User.1" user)',
    TAB + TAB + '(41 "User.2" user)',
    TAB + TAB + '(43 "User.3" user)',
    TAB + TAB + '(45 "User.4" user)',
]:
    A(s)
A(TAB + ")")

# Setup
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

# Nets
for nm, nid in [("GND", 1), ("VCC", 2), ("SDA", 3), ("SCL", 4), ("RDY", 5), ("RST", 6)]:
    A(TAB + f'(net {nid} "{nm}")')
A(TAB + '(net 0 "")')


def footprint(libid, uuid_fp, x, y, rot, layer, descr, tags, properties, pads, attr):
    """Write a complete footprint block."""
    A(TAB + f'(footprint "{libid}"')
    A(TAB + TAB + f'(layer "{layer}")')
    A(TAB + TAB + f'(uuid "{uuid_fp}")')
    A(TAB + TAB + f"(at {x:.2f} {y:.2f} {rot})")
    if descr:
        A(TAB + TAB + f'(descr "{descr}")')
    if tags:
        A(TAB + TAB + f'(tags "{tags}")')
    for pname, pval, px, py, play, hide in properties:
        A(TAB + TAB + f'(property "{pname}" "{pval}"')
        A(TAB + TAB + TAB + f"(at {px:.2f} {py:.2f} 0)")
        A(TAB + TAB + TAB + f'(layer "{play}")')
        if hide:
            A(TAB + TAB + TAB + "(hide yes)")
        A(TAB + TAB + TAB + f'(uuid "{U()}")')
        A(TAB + TAB + TAB + "(effects (font (size 1 1) (thickness 0.15)))")
        A(TAB + TAB + ")")
    if attr:
        A(TAB + TAB + f"(attr {attr})")
    for pnum, ptype, pshape, px, py, psx, psy, drill, play, netid in pads:
        A(TAB + TAB + f'(pad "{pnum}" {ptype} {pshape}')
        A(TAB + TAB + TAB + f"(at {px:.2f} {py:.2f})")
        A(TAB + TAB + TAB + f"(size {psx:.2f} {psy:.2f})")
        if drill > 0:
            A(TAB + TAB + TAB + f"(drill {drill:.2f})")
        A(TAB + TAB + TAB + f"(layers {play})")
        if netid > 0:
            A(TAB + TAB + TAB + f"(net {netid})")
        A(TAB + TAB + TAB + f'(uuid "{U()}")')
        A(TAB + TAB + ")")
    A(TAB + ")")


# ── Pin pads (24x single-pin headers) ──
for prefix, pins, rx in [("JP1", LEFT, J1X), ("JP2", RIGHT, J2X)]:
    for pn in range(1, 13):
        y = P1Y - (pn - 1) * PP
        lb = pins[pn]
        net = pnet(lb)
        footprint(
            libid=PIN_FP,
            uuid_fp=U(),
            x=rx, y=y, rot=0, layer="F.Cu",
            descr=f"Pin {pn}: {lb}",
            tags="pin header",
            properties=[
                ("Reference", f"{prefix}_{pn}", rx, y + 2, "F.SilkS", False),
                ("Value", lb, rx - 2, y, "F.Fab", True),
                ("Datasheet", "~", rx, y, "F.Fab", True),
            ],
            pads=[
                ("1", "thru_hole", "circle", 0, 0, 1.7, 1.7, 1.0, '"*.Cu" "*.Mask"', net),
            ],
            attr="exclude_from_pos_files exclude_from_bom",
        )

# ── FFC connector ──
fy = P1Y + 3.0
ffc_pads = []
for pi in range(6):
    px = -1.25 + pi * 0.5
    nid = [2, 3, 4, 5, 6, 1][pi]
    ffc_pads.append((str(pi + 1), "smd", "rect", px, 0, 0.3, 1.5, 0,
                      '"F.Cu" "F.Paste" "F.Mask"', nid))
footprint(
    libid=FFC_FP,
    uuid_fp=U(),
    x=0, y=fy, rot=0, layer="F.Cu",
    descr="6-pin 0.5mm FFC connector for TPS43",
    tags="FFC FPC TPS43",
    properties=[
        ("Reference", "CON1", 0, fy + 2, "F.SilkS", False),
        ("Value", "TPS43 FFC", 0, fy + 3.5, "F.Fab", True),
        ("Datasheet", "~", 0, fy, "F.Fab", True),
    ],
    pads=ffc_pads,
    attr="smd",
)

# ── Resistors ──
r1_y = fy + 5.0
r2_y = fy + 2.5
rrx = J1X + 3.0
for rname, ry, snet in [("R1", r1_y, 3), ("R2", r2_y, 4)]:
    footprint(
        libid=RES_FP,
        uuid_fp=U(),
        x=rrx, y=ry, rot=90, layer="F.Cu",
        descr="2.2k pull-up",
        tags="resistor 0805",
        properties=[
            ("Reference", rname, rrx, ry + 2, "F.SilkS", False),
            ("Value", "2.2k", rrx, ry - 2, "F.Fab", False),
            ("Datasheet", "~", rrx, ry, "F.Fab", True),
        ],
        pads=[
            ("1", "smd", "rect", -1.0, 0, 1.2, 1.4, 0, '"F.Cu" "F.Paste" "F.Mask"', snet),
            ("2", "smd", "rect", 1.0, 0, 1.2, 1.4, 0, '"F.Cu" "F.Paste" "F.Mask"', 2),
        ],
        attr="smd",
    )

# ── Tracks ──
d8y = P1Y - 10 * PP
d9y = P1Y - 11 * PP
d10y = P1Y - 11 * PP
d16y = P1Y - 10 * PP
vccy = P1Y - 3 * PP
gndy = P1Y - 2 * PP


def TR(x1, y1, x2, y2, w, n):
    A(TAB + f"(segment (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f})"
      f" (width {w:.2f}) (layer \"F.Cu\") (net {n}) (uuid \"{U()}\"))")


segments = [
    # SDA
    (J1X, d8y, J1X + 3, d8y, 0.25, 3),
    (J1X + 3, d8y, J1X + 2, r1_y - 1, 0.25, 3),
    (J1X + 2, r1_y - 1, rrx - 1, r1_y, 0.25, 3),
    (J1X + 2, r1_y - 1, -0.75, r1_y - 1, 0.25, 3),
    (-0.75, r1_y - 1, -0.75, fy, 0.25, 3),
    # SCL
    (J1X, d9y, J1X + 3, d9y, 0.25, 4),
    (J1X + 3, d9y, J1X + 2, r2_y - 1, 0.25, 4),
    (J1X + 2, r2_y - 1, rrx - 1, r2_y, 0.25, 4),
    (J1X + 2, r2_y - 1, -0.25, r2_y - 1, 0.25, 4),
    (-0.25, r2_y - 1, -0.25, fy, 0.25, 4),
    # RDY
    (J2X, d10y, 0, d10y, 0.25, 5),
    (0, d10y, 0, fy + 0.25, 0.25, 5),
    (0, fy + 0.25, 0.25, fy, 0.25, 5),
    # RST
    (J2X, d16y, 0, d16y, 0.25, 6),
    (0, d16y, 0, fy + 0.75, 0.25, 6),
    (0, fy + 0.75, 0.75, fy, 0.25, 6),
    # VCC
    (J2X, vccy, J1X + 4, vccy, 0.5, 2),
    (J1X + 4, vccy, J1X + 4, r1_y, 0.5, 2),
    (J1X + 4, r1_y, rrx + 1, r1_y, 0.5, 2),
    (J1X + 4, vccy, J1X + 4, r2_y, 0.5, 2),
    (J1X + 4, r2_y, rrx + 1, r2_y, 0.5, 2),
    (J1X + 4, vccy, -1.25, vccy, 0.5, 2),
    (-1.25, vccy, -1.25, fy, 0.5, 2),
    # GND
    (J1X, gndy, 1.25, gndy, 0.5, 1),
    (1.25, gndy, 1.25, fy, 0.5, 1),
]

for s in segments:
    TR(*s)

# ── Board outline ──
hw = BW / 2
hh = BH / 2
ol = [(-hw, hh), (hw, hh), (hw, -hh), (-hw, -hh)]
for i in range(4):
    x1, y1 = ol[i]
    x2, y2 = ol[(i + 1) % 4]
    A(TAB + f"(gr_line (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f})"
      f" (layer \"Edge.Cuts\") (width 0.1) (uuid \"{U()}\"))")

# ── Silkscreen ──
silk = [
    ("Temper TPS43 Interposer", 0, hh - 1.5, "1.0 1.0"),
    ("v1.0", 0, hh - 2.8, "0.8 0.8"),
    ("SDA(2)   SCL(3)   RDY(4)   RST(5)", 0, fy - 2.5, "0.8 0.8"),
    ("VCC(1)                     GND(6)", 0, fy - 3.8, "0.6 0.6"),
]
for tx, sx, sy, fs in silk:
    A(TAB + f'(gr_text "{tx}" (at {sx:.2f} {sy:.2f} 0) (layer "F.SilkS")'
      f" (effects (font (size {fs}) (thickness 0.15))) (uuid \"{U()}\"))")

for i in range(12):
    y = P1Y - i * PP
    lb = LEFT[i + 1]
    if lb in ("D8", "D9", "GND"):
        A(TAB + f'(gr_text "{lb}" (at {J1X - 2.5:.2f} {y:.2f} 0)'
          f' (layer "F.SilkS") (effects (font (size 0.6 0.6) (thickness 0.075))) (uuid "{U()}"))')
    rb = RIGHT[i + 1]
    if rb in ("D10", "D16", "VCC"):
        A(TAB + f'(gr_text "{rb}" (at {J2X + 2.5:.2f} {y:.2f} 0)'
          f' (layer "F.SilkS") (effects (font (size 0.6 0.6) (thickness 0.075))) (uuid "{U()}"))')

A(TAB + "(embedded_fonts no)")
A(")")

# ── Write ──
content = "\n".join(lines) + "\n"
with open(OUT, "w") as f:
    f.write(content)

print(f"Generated {OUT} ({len(content)} bytes)")
print(f"Footprints reference: {PIN_FP}, {RES_FP}, {FFC_FP}")
print(f"Board outline: {BW:.0f}x{BH:.0f}mm")
