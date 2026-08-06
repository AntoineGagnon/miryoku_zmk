#!/usr/bin/env python3
"""Generate temper-tps43-interposer.kicad_sch, the netlist twin of the generated PCB.

Plain python3 is enough here: eeschema has no scripting API, so the schematic is emitted as
s-expressions. Symbol definitions are lifted verbatim out of the installed KiCad libraries
rather than transcribed, so the embedded lib_symbols always match the real ones.

The reference designators, footprints, values and nets below must stay identical to
gen_interposer.py, because `kicad-cli pcb drc --schematic-parity` compares them.

  python3 gen_schematic.py && kicad-cli sch upgrade temper-tps43-interposer.kicad_sch
"""

import os
import uuid as uuidlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "temper-tps43-interposer.kicad_sch")
SYM_DIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"

# Deterministic UUIDs: regenerating the file should not produce a spurious git diff.
NS = uuidlib.UUID("6f2b1c40-7a53-4f21-9d8e-000000000000")
SHEET_UUID = str(uuidlib.uuid5(NS, "root-sheet"))


def uid(*parts):
    return str(uuidlib.uuid5(NS, "/".join(str(p) for p in parts)))


# --------------------------------------------------------------------------------------------
# Symbol library extraction
# --------------------------------------------------------------------------------------------


def extract_symbol(lib, name):
    path = os.path.join(SYM_DIR, lib + ".kicad_sym")
    text = open(path).read()
    key = '(symbol "%s"' % name
    i = text.find(key)
    if i < 0:
        raise SystemExit("symbol %s:%s not found in %s" % (lib, name, path))
    depth, j = 0, i
    while True:
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    body = text[i:j + 1]
    # Re-key the definition to the "Lib:Name" form a schematic expects.
    return body.replace(key, '(symbol "%s:%s"' % (lib, name), 1)


def symbol_pins(lib, name):
    """Return {number: (x, y, pin_name, rotation)} in library coordinates (+Y up).

    The rotation is the direction the pin body runs *into* the symbol, so the wire stub has
    to leave in the opposite direction.
    """
    import re
    body = extract_symbol(lib, name)
    pins = {}
    for m in re.finditer(
            r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\).*?'
            r'\(name "([^"]*)".*?\(number "([^"]*)"', body, re.S):
        pins[m.group(5)] = (float(m.group(1)), float(m.group(2)),
                            m.group(4), int(m.group(3)))
    return pins


# Wire stub direction and label angle for each pin rotation, in schematic coordinates
# (+Y downward). Key is the pin's own rotation.
STUB_DIR = {0: (-1, 0, 180), 180: (1, 0, 0), 90: (0, 1, 270), 270: (0, -1, 90)}


# --------------------------------------------------------------------------------------------
# Component table. Keep in lockstep with gen_interposer.py.
# --------------------------------------------------------------------------------------------

# Azoteq TPS43 J1 pinout, from the ProxSense Standard Trackpad Module datasheet, revision 1.06,
# August 2025. Do not take this from the 2016 rev 1.02 PDF still mirrored on distributor sites:
# rev 1.04 (December 2022) changed this very table, and the old one has SDA and NRST swapped.
TPS43_J1 = {1: "RDY", 2: "RST", 3: "GND", 4: "VCC", 5: "SCL", 6: "SDA"}

# The FFC cable this board is built for reverses the conductor order end to end, so CON1 pin N
# mates with TPS43 pin 7-N. Verify with a meter before fabbing; see README.
#
# Setting this False produces the correct netlist for a straight-through cable, but it is NOT a
# drop-in change: the escape-lane order flips, which moves the pull-ups to the east side and
# swaps which header column carries I2C (so the ZMK overlay changes too). gen_interposer.py
# refuses to route that variant rather than emitting a board with plausible-looking bad routing.
CON1_MIRRORED = True


def con1_nets():
    """CON1's pin-to-net map, derived from the trackpad's pinout and the cable's mapping."""
    nets = {str(n): TPS43_J1[7 - n if CON1_MIRRORED else n] for n in range(1, 7)}
    # The two solder tabs are mechanical retention. Grounding them is the usual practice and
    # gives the shell a return path.
    nets["MP"] = "GND"
    return nets


# "fields" is where the visible Reference and Value text go, relative to the symbol origin.
# Both are placed clear of the symbol body and of the wire stubs, which all leave to the left
# (connectors) or vertically (resistors).
COMPONENTS = [
    dict(ref="JP1", lib="Connector_Generic", name="Conn_01x12", at=(69.85, 88.9),
         value="Pro Micro L", fields=((0, -19.05), (0, -16.51)), justify="center",
         footprint="Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical",
         desc="Left header row of the nice!nano, pass-through",
         nets={"3": "GND", "4": "GND", "11": "SDA", "12": "SCL"}),
    dict(ref="JP2", lib="Connector_Generic", name="Conn_01x12", at=(114.3, 88.9),
         value="Pro Micro R", fields=((0, -19.05), (0, -16.51)), justify="center",
         footprint="Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical",
         desc="Right header row of the nice!nano, pass-through",
         nets={"2": "GND", "4": "VCC", "11": "RST", "12": "RDY"}),
    dict(ref="CON1", lib="Connector_Generic_MountingPin", name="Conn_01x06_MountingPin",
         at=(180.34, 81.28), value="FFC 1x06 0.5mm",
         fields=((0, -8.89), (0, -11.43)), justify="center",
         footprint="Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal",
         desc="Azoteq TPS43 trackpad, 6-pos 0.5mm FFC",
         nets=con1_nets()),
    dict(ref="R1", lib="Device", name="R", at=(147.32, 63.5), value="2.2k",
         fields=((2.54, -1.27), (2.54, 1.27)), justify="left",
         footprint="Resistor_SMD:R_0805_2012Metric", desc="SDA pull-up",
         nets={"1": "VCC", "2": "SDA"}),
    dict(ref="R2", lib="Device", name="R", at=(162.56, 63.5), value="2.2k",
         fields=((2.54, -1.27), (2.54, 1.27)), justify="left",
         footprint="Resistor_SMD:R_0805_2012Metric", desc="SCL pull-up",
         nets={"1": "VCC", "2": "SCL"}),
]

# What each pass-through header pin actually is, so the schematic documents the Pro Micro
# pinout instead of showing twenty anonymous no-connects.
JP1_PINOUT = ["D1/TX", "D0/RX", "GND", "GND", "D2", "D3", "D4/A6", "D5",
              "D6/A7", "D7", "D8/A8 (P1.04)", "D9/A9 (P0.09)"]
JP2_PINOUT = ["RAW", "GND", "RST", "VCC", "D21/A3", "D20/A2", "D19/A1", "D18/A0",
              "D15/SCK", "D14/MISO", "D16/MOSI (P1.06)", "D10/A10 (P0.11)"]

STUB = 5.08


def netlist():
    """The single source of truth for which pad carries which net.

    Yields (component, pad_number, net_name, connected) for every pad on the board.
    gen_interposer.py imports this so the PCB and the schematic cannot drift apart.
    Unconnected pads get the same auto-generated name KiCad's own "Update PCB from
    Schematic" would assign, which is what makes --schematic-parity come out clean.
    """
    for c in COMPONENTS:
        pins = symbol_pins(c["lib"], c["name"])
        for number in sorted(pins, key=lambda n: sort_key((n, None))):
            pin_name = pins[number][2]
            net = c["nets"].get(number)
            if net is not None:
                yield c, number, net, True
            else:
                yield c, number, "unconnected-(%s-%s-Pad%s)" % (
                    c["ref"], pin_name.replace("~", ""), number), False


def build():
    out = []
    a = out.append

    a('(kicad_sch')
    a('\t(version 20250114)')
    a('\t(generator "gen_schematic.py")')
    a('\t(generator_version "9.0")')
    a('\t(uuid "%s")' % SHEET_UUID)
    a('\t(paper "A4")')
    a('\t(title_block')
    a('\t\t(title "Temper TPS43 Interposer")')
    a('\t\t(rev "1.0")')
    a('\t\t(comment 1 "nice!nano v2 pass-through with Azoteq TPS43 trackpad breakout")')
    a('\t\t(comment 2 "Nets: GND VCC SDA SCL RDY RST. All other Pro Micro pins pass through.")')
    a('\t)')

    # ---- lib_symbols -----------------------------------------------------------------
    a('\t(lib_symbols')
    seen = set()
    for c in COMPONENTS:
        key = (c["lib"], c["name"])
        if key in seen:
            continue
        seen.add(key)
        for line in extract_symbol(*key).splitlines():
            a('\t\t' + line.strip('\n'))
    a('\t)')

    # ---- wires, labels, no-connects, symbols -----------------------------------------
    for c in COMPONENTS:
        pins = symbol_pins(c["lib"], c["name"])
        sx, sy = c["at"]

        for number in sorted(pins, key=lambda n: sort_key((n, None))):
            px, py, _, rot = pins[number]
            # Schematic Y grows downward, library Y grows upward.
            x, y = sx + px, sy - py
            net = c["nets"].get(number)
            if net is None:
                a('\t(no_connect')
                a('\t\t(at %s %s)' % (fmt(x), fmt(y)))
                a('\t\t(uuid "%s")' % uid(c["ref"], "nc", number))
                a('\t)')
                continue

            dx, dy, angle = STUB_DIR[rot]
            ex, ey = x + dx * STUB, y + dy * STUB
            wire(a, (x, y), (ex, ey), uid(c["ref"], "w", number))
            label(a, net, (ex, ey), angle, uid(c["ref"], "l", number))

        symbol(a, c, pins)

    # ---- documentation text ----------------------------------------------------------
    notes = [
        "JP1 / JP2 reproduce the nice!nano v2 (Pro Micro) footprint one for one.",
        "Every pin not listed below is a bare pass-through: plated hole, no copper attached.",
        "",
        "  JP1.11  D8  / P1.04  ->  SDA      JP2.12  D10 / P0.11  ->  RDY",
        "  JP1.12  D9  / P0.09  ->  SCL      JP2.11  D16 / P1.06  ->  RST",
        "  JP1.3, JP1.4, JP2.2  ->  GND      JP2.4   VCC (3.3V)   ->  VCC",
        "",
        "CON1 is wired as the MIRROR of the trackpad's own connector, because the FFC cable",
        "reverses the conductor order end to end. TPS43 J1 (datasheet rev 1.06, Aug 2025) is",
        "1:RDY 2:NRST 3:GND 4:VDDHI 5:SCL 6:SDA, so CON1 pin N carries TPS43 pin 7-N.",
        "VERIFY the cable before assembly: ring out pin 1 to pin 6 with a meter. If it is a",
        "straight-through cable instead, this board is wrong and must be re-fabbed.",
        "",
        "R1/R2 are the 2.2k I2C bus pull-ups. CON1 MP is the pair of mechanical solder tabs,",
        "tied to GND. B.Cu is a GND plane carrying the VCC, SCL-to-R2 and RST crossings.",
    ]
    for n, line in enumerate(notes):
        if not line:
            continue
        a('\t(text "%s"' % line.replace('"', '\\"'))
        a('\t\t(exclude_from_sim no)')
        a('\t\t(at 20.32 %s 0)' % fmt(127.0 + n * 4.0))
        a('\t\t(effects (font (size 1.6 1.6)) (justify left bottom))')
        a('\t\t(uuid "%s")' % uid("note", n))
        a('\t)')

    a('\t(sheet_instances')
    a('\t\t(path "/"')
    a('\t\t\t(page "1")')
    a('\t\t)')
    a('\t)')
    a('\t(embedded_fonts no)')
    a(')')
    return "\n".join(out) + "\n"


def sort_key(item):
    number = item[0]
    return (0, int(number)) if number.isdigit() else (1, number)


def fmt(v):
    return ("%.4f" % v).rstrip("0").rstrip(".") or "0"


def wire(a, p0, p1, u):
    a('\t(wire')
    a('\t\t(pts (xy %s %s) (xy %s %s))' % (fmt(p0[0]), fmt(p0[1]), fmt(p1[0]), fmt(p1[1])))
    a('\t\t(stroke (width 0) (type default))')
    a('\t\t(uuid "%s")' % u)
    a('\t)')


def label(a, name, pos, angle, u):
    """Global labels, deliberately. A local label on the root sheet is scoped to that sheet
    and comes out of the netlist as "/GND", which would never match the board's "GND"."""
    justify = "right" if angle == 180 else "left"
    a('\t(global_label "%s"' % name)
    a('\t\t(shape bidirectional)')
    a('\t\t(at %s %s %d)' % (fmt(pos[0]), fmt(pos[1]), angle))
    a('\t\t(effects (font (size 1.27 1.27)) (justify %s))' % justify)
    a('\t\t(uuid "%s")' % u)
    a('\t)')


def symbol(a, c, pins):
    sx, sy = c["at"]
    (rdx, rdy), (vdx, vdy) = c["fields"]
    a('\t(symbol')
    a('\t\t(lib_id "%s:%s")' % (c["lib"], c["name"]))
    a('\t\t(at %s %s 0)' % (fmt(sx), fmt(sy)))
    a('\t\t(unit 1)')
    a('\t\t(exclude_from_sim no)')
    a('\t\t(in_bom yes)')
    a('\t\t(on_board yes)')
    a('\t\t(dnp no)')
    a('\t\t(uuid "%s")' % uid(c["ref"], "sym"))
    for name, value, hide, dx, dy in (
            ("Reference", c["ref"], False, rdx, rdy),
            ("Value", c["value"], False, vdx, vdy),
            ("Footprint", c["footprint"], True, vdx, vdy + 2.54),
            ("Datasheet", "~", True, vdx, vdy + 5.08),
            ("Description", c["desc"], True, vdx, vdy + 7.62),
    ):
        a('\t\t(property "%s" "%s"' % (name, value))
        a('\t\t\t(at %s %s 0)' % (fmt(sx + dx), fmt(sy + dy)))
        # KiCad only accepts left/right/top/bottom/mirror here; centred is the default and
        # has to be spelled as the absence of a justify token.
        just = "" if c["justify"] == "center" else " (justify %s)" % c["justify"]
        a('\t\t\t(effects (font (size 1.27 1.27))%s%s)'
          % (just, " (hide yes)" if hide else ""))
        a('\t\t)')
    for number in sorted(pins, key=lambda n: sort_key((n, None))):
        a('\t\t(pin "%s" (uuid "%s"))' % (number, uid(c["ref"], "pin", number)))
    a('\t\t(instances')
    a('\t\t\t(project "temper-tps43-interposer"')
    a('\t\t\t\t(path "/%s"' % SHEET_UUID)
    a('\t\t\t\t\t(reference "%s") (unit 1)' % c["ref"])
    a('\t\t\t\t)')
    a('\t\t\t)')
    a('\t\t)')
    a('\t)')


if __name__ == "__main__":
    with open(OUT, "w") as fh:
        fh.write(build())
    print("wrote %s" % OUT)
