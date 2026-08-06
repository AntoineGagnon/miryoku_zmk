#!/usr/bin/env python3
"""Generate temper-tps43-interposer.kicad_pcb from scratch with the KiCad pcbnew API.

Run with KiCad's bundled interpreter, which is the only one that has pcbnew:

  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
      gen_interposer.py

The board is described entirely in the "spec frame" used by PCB_SPEC.md: X is centred on the
board, +Y points toward the trackpad (i.e. up when looking at the front of the board). KiCad's
internal Y axis points down, so every coordinate goes through spec_to_kicad() exactly once.

Nothing in the resulting .kicad_pcb should ever be hand-edited. Change this script and re-run.
"""

import json
import os
import sys

import pcbnew
from pcbnew import VECTOR2I

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# The shared PCB/schematic netlist.
from gen_schematic import CON1_MIRRORED, COMPONENTS, TPS43_J1, netlist  # noqa: E402

# --------------------------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_FILE = os.path.join(HERE, "temper-tps43-interposer.kicad_pcb")
PROJECT_FILE = os.path.join(HERE, "temper-tps43-interposer.kicad_pro")

FP_DIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
LIB_HEADER = "Connector_PinHeader_2.54mm"
LIB_FFC = "Connector_FFC-FPC"
LIB_RES = "Resistor_SMD"

FP_HEADER = "PinHeader_1x12_P2.54mm_Vertical"
FP_FFC = "Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal"
FP_RES = "R_0805_2012Metric"

# --------------------------------------------------------------------------------------------
# Geometry constants, all in the spec frame, all millimetres
# --------------------------------------------------------------------------------------------

# Where the spec origin lands on the KiCad page.
PAGE_X, PAGE_Y = 100.0, 100.0

# Board size is set by the Temper PCB, measured from raeedcho/temper pcb/temper.kicad_pcb:
#   - controller header columns at X 170.43 and 185.67, so the interposer centres on X 178.05
#   - the adjacent choc hotswap sockets (SW5/SW10/SW15) end at X 167.49, only 1.60 mm from the
#     nice!nano footprint, which caps the half-width at 178.05 - 167.49 - 0.5 = 10.06 mm
#   - Temper's own right board edge is at X 188.29, so 10.0 mm also stays on the board
# Hence 20.0 mm wide. This is barely more than the nice!nano's own 18 mm, and it is a hard
# limit: choc switches stand ~4.7 mm tall against an interposer sitting ~2-3 mm up.
BOARD_X0, BOARD_X1 = -10.0, 10.0
BOARD_Y1 = 23.5               # north edge, 3.66 mm inside Temper's top edge
BOARD_Y0 = -16.5              # south edge of the two legs, minimum for pad edge clearance
BOARD_THICKNESS = 1.0

# Temper's nice!view header J2 spans X 171.63..184.48, Y 86.33..92.16, which in this frame is
# X -6.42..+6.43 starting at Y -15.21, i.e. level with header pin 12. Any board that reaches
# pin 12 overlaps it, so the south edge is notched: full width down to NOTCH_Y, then two legs
# that carry the pin 12 pads and sit outside J2's width.
NOTCH_Y = -15.2
NOTCH_X = 6.35                # legs are |X| 6.35..10.0; pin 12 pad edge is at 6.77

PITCH = 2.54                  # header pin pitch
ROW_DX = 7.62                 # half of the 15.24 mm row spacing
PIN1_Y = 12.70                # spec Y of header pin 1

CON1_X, CON1_Y = 0.0, 19.15   # FH12 origin
# The pull-ups end up on opposite sides of the board, which looks arbitrary but is forced. The
# escape corridor makes SDA the outermost west trunk, so SDA is fenced west of SCL for its whole
# length: no single spot can reach both on F.Cu. R1 therefore goes west of the JP1 pad column,
# where SDA can reach it over the top of the header pads, and R2 goes in the centre channel,
# where SCL can reach it without crossing anything. Both VCC pads are fed from the B.Cu side.
R1_X, R1_Y = -8.50, 16.60     # SDA pull-up, west of the JP1 column
R2_X, R2_Y = 2.50, 7.00       # SCL pull-up, centre channel (under the nice!nano)

# FH12 pad geometry, derived from the library footprint and asserted below.
FFC_PAD_Y = CON1_Y + 1.85     # spec Y of the six signal pads
FFC_PAD_X = {1: -1.25, 2: -0.75, 3: -0.25, 4: 0.25, 5: 0.75, 6: 1.25}

# The three escape lanes in the 1.50 mm corridor between the signal pads (south edge 20.35)
# and the MP solder tabs (north edge 18.85). Three 0.20 mm tracks with 0.225 mm gaps.
LANE_A = 20.025               # outermost: CON1.1 SDA west, CON1.6 RDY east
LANE_B = 19.600               # middle:    CON1.2 SCL west, CON1.5 RST east
LANE_C = 19.175               # innermost: CON1.3 VCC west, CON1.4 GND east

# Each lane runs at its own Y until it reaches its own trunk X and turns square. No diagonals:
# a lane that dives toward its trunk cuts the corner off the lane below it, and at 0.425 mm
# lane spacing there is no room for that.
#
# The lane order is dictated by the pad order, not by choice: the pad nearest the centre has to
# take the innermost lane so it can duck under its neighbours' drops. That in turn fixes the
# trunk order, because a lane turning south blocks every lane below it from going further out.
# Lane A therefore turns furthest from the centre and lane C nearest to it.

W_THIN = 0.20                 # corridor and signal tracks
W_SIG = 0.20                  # signal nets keep one width end to end
W_PWR = 0.50                  # VCC and GND once clear of the corridor

# Vertical trunks, ordered outward-to-inward to match the lane order above. On a 20 mm board
# there is no room outside the header columns, so all six run in the 2.22 mm band between the
# header pads (|X| 6.77) and the connector's mounting tabs (|X| 4.05), on 0.6 mm centres.
X_SDA = -6.35                 # lane A west, outermost
X_SCL = -5.75                 # lane B west
X_VCC = -5.15                 # lane C west, innermost, hops to B.Cu immediately
X_GND = 5.15                  # lane C east, innermost, joins the mounting tabs
X_RST = 5.75                  # lane B east
X_RDY = 6.35                  # lane A east, outermost

# Where the layer changes happen.
Y_VCC_VIA = 15.50
Y_TAB_VIA = 15.00
Y_TABS = 17.75                # the mounting tab centre line
MP_TAB_X = 3.15
# SDA crosses the header column above the pads to reach R1; SCL runs down the channel to R2.
Y_SDA_STUB = 15.6875          # = R1_Y - 0.9125, R1's south pad
Y_SCL_STUB = 6.0875           # = R2_Y - 0.9125, R2's south pad
VCC_HUB = (-3.00, 13.00)      # F.Cu -> B.Cu, clear of the crowded trunk band
VCC_TAP_R1 = (-8.50, 19.00)   # B.Cu -> F.Cu, north of R1
VCC_TAP_R2 = (2.50, 10.00)    # B.Cu -> F.Cu, north of R2

# Pin 12 sits at Y -15.24, below the notch line, so its pad is only reachable inside a leg.
# The two nets that land there cross to the header column above the notch and drop in from
# there; running straight down at the trunk X would leave the board.
Y_PIN12_CROSS = -14.00

VIA_D, VIA_DRILL = 0.60, 0.30
VIA_D_PWR, VIA_DRILL_PWR = 0.80, 0.40

ZONE_INSET = 0.50

# Fabrication constraints. Chosen to sit inside every common cheap 2-layer process; the
# tightest thing on the board is the 0.20 mm connector escape on 0.40 mm centres.
RULES = {
    "min_clearance": 0.20,
    "min_track_width": 0.20,
    "min_via_diameter": 0.60,
    "min_via_annular_width": 0.13,
    "min_through_hole_diameter": 0.30,
    "min_copper_edge_clearance": 0.40,
    "min_hole_clearance": 0.25,
    "min_hole_to_hole": 0.25,
    "min_silk_clearance": 0.15,
    "min_text_height": 0.50,
    "min_text_thickness": 0.08,
    "min_connection": 0.20,
}

# Anything that could ship a broken board is promoted to an error so that
# `kicad-cli pcb drc --exit-code-violations` actually gates on it.
SEVERITY_OVERRIDES = {
    "connection_width": "error",
    "duplicate_footprints": "error",
    "extra_footprint": "error",
    "footprint_type_mismatch": "error",
    "hole_to_hole": "error",
    "holes_co_located": "error",
    "missing_footprint": "error",
    "net_conflict": "error",
    "track_dangling": "error",
    "via_dangling": "error",
    "npth_inside_courtyard": "ignore",
    "pth_inside_courtyard": "ignore",
    "missing_courtyard": "ignore",
    # We deliberately delete the 1x12 headers' silkscreen outline, which otherwise runs off
    # all three nearby board edges at this size. That makes the board copies differ from the
    # library copies by design, on every build. The rule exists to catch accidental drift,
    # and there is none here: every footprint is reloaded from the library each run.
    "lib_footprint_mismatch": "ignore",
}

# --------------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------------


def mm(v):
    return pcbnew.FromMM(v)


def xy(sx, sy):
    """Spec frame -> KiCad internal units."""
    return VECTOR2I(mm(PAGE_X + sx), mm(PAGE_Y - sy))


def pin_y(n):
    """Spec Y of header pin n (1-based, pin 1 at the top)."""
    return PIN1_Y - (n - 1) * PITCH


def load_fp(lib, name):
    path = os.path.join(FP_DIR, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        sys.exit("could not load %s:%s from %s" % (lib, name, path))
    return fp


class Builder(object):
    def __init__(self):
        self.board = pcbnew.BOARD()
        self.nets = {}
        self.fps = {}

    # -- board level ---------------------------------------------------------------------

    def setup_board(self):
        b = self.board
        b.SetCopperLayerCount(2)
        ds = b.GetDesignSettings()
        ds.SetBoardThickness(mm(BOARD_THICKNESS))
        ds.SetAuxOrigin(xy(0, 0))
        ds.SetGridOrigin(xy(0, 0))

        ds.m_MinClearance = mm(RULES["min_clearance"])
        ds.m_TrackMinWidth = mm(RULES["min_track_width"])
        ds.m_ViasMinSize = mm(RULES["min_via_diameter"])
        ds.m_ViasMinAnnularWidth = mm(RULES["min_via_annular_width"])
        ds.m_MinThroughDrill = mm(RULES["min_through_hole_diameter"])
        ds.m_CopperEdgeClearance = mm(RULES["min_copper_edge_clearance"])
        ds.m_HoleClearance = mm(RULES["min_hole_clearance"])
        ds.m_HoleToHoleMin = mm(RULES["min_hole_to_hole"])
        ds.m_SilkClearance = mm(RULES["min_silk_clearance"])
        ds.m_MinSilkTextHeight = mm(RULES["min_text_height"])
        ds.m_MinSilkTextThickness = mm(RULES["min_text_thickness"])
        ds.m_MinConn = mm(RULES["min_connection"])
        ds.m_MinResolvedSpokes = 2

        nc = ds.m_NetSettings.GetDefaultNetclass()
        nc.SetClearance(mm(0.20))
        nc.SetTrackWidth(mm(0.25))
        nc.SetViaDiameter(mm(VIA_D))
        nc.SetViaDrill(mm(VIA_DRILL))

        for w in (0.0, W_SIG, 0.25, W_PWR):
            ds.m_TrackWidthList.append(mm(w))
        for d, dr in ((0.0, 0.0), (VIA_D, VIA_DRILL), (VIA_D_PWR, VIA_DRILL_PWR)):
            ds.m_ViasDimensionsList.append(pcbnew.VIA_DIMENSION(mm(d), mm(dr)))

        enabled = pcbnew.LSET()
        for layer in (
            pcbnew.F_Cu, pcbnew.B_Cu,
            pcbnew.F_Mask, pcbnew.B_Mask,
            pcbnew.F_Paste, pcbnew.B_Paste,
            pcbnew.F_SilkS, pcbnew.B_SilkS,
            pcbnew.F_CrtYd, pcbnew.B_CrtYd,
            pcbnew.F_Fab, pcbnew.B_Fab,
            pcbnew.Edge_Cuts, pcbnew.Margin,
            pcbnew.Cmts_User, pcbnew.Dwgs_User,
            pcbnew.Eco1_User, pcbnew.Eco2_User,
        ):
            enabled.addLayer(layer)
        b.SetEnabledLayers(enabled)
        b.SetVisibleLayers(enabled)

    def net(self, name):
        if name not in self.nets:
            n = pcbnew.NETINFO_ITEM(self.board, name)
            self.board.Add(n)
            self.nets[name] = n
        return self.nets[name]

    # -- primitives ----------------------------------------------------------------------

    def edge(self, p0, p1):
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(xy(*p0))
        s.SetEnd(xy(*p1))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.05))
        self.board.Add(s)

    def track(self, p0, p1, net, width, layer=pcbnew.F_Cu):
        t = pcbnew.PCB_TRACK(self.board)
        t.SetStart(xy(*p0))
        t.SetEnd(xy(*p1))
        t.SetWidth(mm(width))
        t.SetLayer(layer)
        t.SetNet(self.net(net))
        self.board.Add(t)
        return t

    def path(self, points, net, width, layer=pcbnew.F_Cu):
        """Route a polyline. `points` may carry per-segment widths as (x, y, width)."""
        w = width
        for a, b in zip(points, points[1:]):
            if len(b) == 3:
                w = b[2]
            self.track(a[:2], b[:2], net, w, layer)

    def via(self, pos, net, diameter=VIA_D, drill=VIA_DRILL):
        v = pcbnew.PCB_VIA(self.board)
        v.SetPosition(xy(*pos))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetWidth(mm(diameter))
        v.SetDrill(mm(drill))
        v.SetNet(self.net(net))
        self.board.Add(v)
        return v

    def text(self, s, pos, size, layer, thickness=None, bold=False, mirror=False):
        t = pcbnew.PCB_TEXT(self.board)
        t.SetText(s)
        t.SetPosition(xy(*pos))
        t.SetLayer(layer)
        t.SetTextSize(VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(thickness if thickness else size * 0.15))
        t.SetBold(bold)
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        if mirror:
            t.SetMirrored(True)
        self.board.Add(t)
        return t

    # -- footprints ----------------------------------------------------------------------

    def place(self, ref, lib, name, pos, rotation, attrs=None):
        fp = load_fp(lib, name)
        self.board.Add(fp)
        # FootprintLoad returns a bare name, so restore the library nickname. Without it
        # DRC's schematic parity reports every footprint as mismatched.
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetPosition(xy(*pos))
        if rotation:
            fp.SetOrientationDegrees(rotation)
        if attrs is not None:
            fp.SetAttributes(fp.GetAttributes() | attrs)
        self.fps[ref] = fp
        return fp

    def pad(self, ref, number):
        for p in self.fps[ref].Pads():
            if p.GetNumber() == str(number):
                return p
        sys.exit("no pad %s on %s" % (number, ref))

    def pads(self, ref, number):
        return [p for p in self.fps[ref].Pads() if p.GetNumber() == str(number)]

    def assign(self, ref, number, net):
        for p in self.pads(ref, number):
            p.SetNet(self.net(net))

    def pad_spec_pos(self, ref, number):
        p = self.pad(ref, number)
        pos = p.GetPosition()
        return (pcbnew.ToMM(pos.x) - PAGE_X, PAGE_Y - pcbnew.ToMM(pos.y))

    def strip_silk(self, ref):
        """Drop a footprint's own silkscreen outline.

        The 1x12 header outline is drawn for a board with room around it; on a 20 mm-wide
        interposer it runs off both side edges and past the south edge. The pin-1 markers and
        labels drawn by silkscreen() replace it.
        """
        fp = self.fps[ref]
        for item in list(fp.GraphicalItems()):
            if item.GetLayer() == pcbnew.F_SilkS:
                fp.Remove(item)

    def move_field(self, ref, field, pos, size, layer=pcbnew.F_SilkS, hide=False):
        item = self.fps[ref].Reference() if field == "ref" else self.fps[ref].Value()
        item.SetPosition(xy(*pos))
        item.SetTextSize(VECTOR2I(mm(size), mm(size)))
        item.SetTextThickness(mm(max(0.1, size * 0.15)))
        item.SetLayer(layer)
        item.SetVisible(not hide)


# --------------------------------------------------------------------------------------------
# Board construction
# --------------------------------------------------------------------------------------------


def build():
    B = Builder()
    B.setup_board()

    # ---- outline ----------------------------------------------------------------------
    # Full width down to NOTCH_Y, then two legs carrying the pin 12 pads. The notch is what
    # keeps the board off Temper's nice!view header.
    corners = [
        (BOARD_X0, BOARD_Y1), (BOARD_X1, BOARD_Y1),
        (BOARD_X1, BOARD_Y0), (NOTCH_X, BOARD_Y0),
        (NOTCH_X, NOTCH_Y), (-NOTCH_X, NOTCH_Y),
        (-NOTCH_X, BOARD_Y0), (BOARD_X0, BOARD_Y0),
    ]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        B.edge(a, b)

    # ---- footprints ------------------------------------------------------------------
    # The pin header footprint's origin is pin 1 and its pins march along local +Y, which
    # maps to spec -Y at rotation 0. So placing the origin at pin 1 is all that is needed.
    # Through-hole headers are hand-soldered, so keep them out of the pick-and-place file.
    # They stay in the BOM: they still have to be ordered.
    hdr_attrs = pcbnew.FP_EXCLUDE_FROM_POS_FILES
    B.place("JP1", LIB_HEADER, FP_HEADER, (-ROW_DX, PIN1_Y), 0, hdr_attrs)
    B.place("JP2", LIB_HEADER, FP_HEADER, (ROW_DX, PIN1_Y), 0, hdr_attrs)

    # FH12 signal pads sit at footprint-local -Y, so rotation 0 points the opening and the
    # pads at spec +Y: the cable exits straight over the top edge toward the trackpad.
    B.place("CON1", LIB_FFC, FP_FFC, (CON1_X, CON1_Y), 0)

    # 0805 at 270 degrees puts pad 1 north and pad 2 south. Pad 1 is the VCC end, which is
    # also how the schematic draws it: pull-up to the rail at the top, signal at the bottom.
    B.place("R1", LIB_RES, FP_RES, (R1_X, R1_Y), 270)
    B.place("R2", LIB_RES, FP_RES, (R2_X, R2_Y), 270)

    # Values and descriptions come from the schematic table so the two stay identical.
    for comp in COMPONENTS:
        B.fps[comp["ref"]].SetValue(comp["value"])
        B.fps[comp["ref"]].SetLibDescription(comp["desc"])
        # The parity check compares the "Description" field, not the library description.
        B.fps[comp["ref"]].SetField("Description", comp["desc"])

    verify_footprint_geometry(B)

    # ---- nets ------------------------------------------------------------------------
    # Driven entirely from gen_schematic.netlist(), including the auto-generated
    # unconnected-(...) names that KiCad gives no-connect pins. Pass-through header pins are
    # plated holes on a net of their own: no copper is attached to them anywhere.
    # CON1's two MP tabs are mechanical retention only and stay unconnected too.
    assigned = 0
    for comp, number, net, _connected in netlist():
        B.assign(comp["ref"], number, net)
        assigned += 1
    print("assigned %d pads across %d nets" % (assigned, len(B.nets)))

    verify_pinout(B)

    route(B)
    ground_zone(B)
    silkscreen(B)

    verify_clearances(B)

    # Saving with settings lets pcbnew regenerate the .kicad_pro in its own native schema
    # from the design settings above, so the project file and the board can never drift.
    pcbnew.SaveBoard(BOARD_FILE, B.board)
    patch_project()
    print("wrote %s" % BOARD_FILE)
    print("  footprints %d  tracks %d  vias %d  zones %d" % (
        len(B.board.GetFootprints()),
        len([t for t in B.board.GetTracks() if t.GetClass() == "PCB_TRACK"]),
        len([t for t in B.board.GetTracks() if t.GetClass() == "PCB_VIA"]),
        len(B.board.Zones())))


def patch_project():
    """pcbnew serialises the design rules but not the DRC severities, so fix those up in
    place. Everything else in the .kicad_pro comes straight from setup_board()."""
    with open(PROJECT_FILE) as fh:
        pro = json.load(fh)

    sev = pro["board"]["design_settings"]["rule_severities"]
    for key, value in SEVERITY_OVERRIDES.items():
        if key in sev:
            sev[key] = value
        else:
            print("  note: unknown DRC rule %r, skipped" % key)

    with open(PROJECT_FILE, "w") as fh:
        json.dump(pro, fh, indent=2, sort_keys=True)
        fh.write("\n")

    rules = pro["board"]["design_settings"]["rules"]
    for key, want in RULES.items():
        got = rules.get(key)
        assert got is not None and abs(got - want) < 1e-6, \
            "design rule %s serialised as %r, expected %r" % (key, got, want)


def route(B):
    pad_y = FFC_PAD_Y

    # ---- west group: SDA (lane A), SCL (lane B), VCC (lane C) --------------------------

    # SDA: CON1.1 -> lane A -> trunk south -> JP1.11. The stub to R1 crosses the header column
    # at Y +15.69, which is 2.1 mm clear of JP1 pin 1's pad, so no via is needed.
    B.path([
        (FFC_PAD_X[1], pad_y),
        (FFC_PAD_X[1], LANE_A),
        (X_SDA, LANE_A),
        (X_SDA, pin_y(11)),
        (-ROW_DX, pin_y(11)),
    ], "SDA", W_SIG)
    B.path([(X_SDA, Y_SDA_STUB), (R1_X, Y_SDA_STUB)], "SDA", W_SIG)

    # SCL: CON1.2 -> lane B -> trunk south -> JP1.12, with a stub east into the channel for R2.
    # Nothing crosses it there: SDA's trunk is west, and VCC's ends at its via.
    B.path([
        (FFC_PAD_X[2], pad_y),
        (FFC_PAD_X[2], LANE_B),
        (X_SCL, LANE_B),
        (X_SCL, Y_PIN12_CROSS),
        (-ROW_DX, Y_PIN12_CROSS),
        (-ROW_DX, pin_y(12)),
    ], "SCL", W_SIG)
    B.path([(X_SCL, Y_SCL_STUB), (R2_X, Y_SCL_STUB)], "SCL", W_SIG)

    # VCC: lane C is the innermost lane, boxed in between the SCL trunk and the connector's
    # west mounting tab, so it cannot travel on F.Cu at all. It drops to B.Cu immediately and
    # fans out from there to JP2.4 and to both pull-up VCC pads.
    B.path([
        (FFC_PAD_X[3], pad_y),
        (FFC_PAD_X[3], LANE_C),
        (X_VCC, LANE_C),
        (X_VCC, VCC_HUB[1]),
        VCC_HUB,
    ], "VCC", W_THIN)
    vcc_hub = VCC_HUB
    B.via(vcc_hub, "VCC", VIA_D_PWR, VIA_DRILL_PWR)
    # Chain hub -> R2 tap -> JP2.4 rather than fanning both out of the hub. Two spurs leaving
    # the hub only 8 degrees apart pinch a long thin wedge of zone between them, which DRC
    # reports as a copper sliver. The R1 spur heads the opposite way, so it is fine.
    B.track(vcc_hub, VCC_TAP_R2, "VCC", W_PWR, pcbnew.B_Cu)
    B.track(VCC_TAP_R2, (ROW_DX, pin_y(4)), "VCC", W_PWR, pcbnew.B_Cu)
    B.track(vcc_hub, VCC_TAP_R1, "VCC", W_PWR, pcbnew.B_Cu)
    for tap, res_x, res_y in ((VCC_TAP_R1, R1_X, R1_Y), (VCC_TAP_R2, R2_X, R2_Y)):
        B.via(tap, "VCC", VIA_D_PWR, VIA_DRILL_PWR)
        B.track(tap, (res_x, res_y + 0.9125), "VCC", W_PWR)

    # ---- east group: RDY (lane A), RST (lane B), GND (lane C) --------------------------

    # RDY takes the outer trunk, so it has to serve the more northern of the two GPIO pins it
    # could reach, otherwise the inner trunk's jog would cut across it. JP2.12 is the southern
    # one, so RDY continues past JP2.11 and RST hops under it on B.Cu. Keeping RDY on D10 and
    # RST on D16 this way is what leaves the ZMK overlay untouched.
    B.path([
        (FFC_PAD_X[6], pad_y),
        (FFC_PAD_X[6], LANE_A),
        (X_RDY, LANE_A),
        (X_RDY, Y_PIN12_CROSS),
        (ROW_DX, Y_PIN12_CROSS),
        (ROW_DX, pin_y(12)),
    ], "RDY", W_SIG)

    B.path([
        (FFC_PAD_X[5], pad_y),
        (FFC_PAD_X[5], LANE_B),
        (X_RST, LANE_B),
        (X_RST, pin_y(11)),
    ], "RST", W_SIG)
    B.via((X_RST, pin_y(11)), "RST")
    B.track((X_RST, pin_y(11)), (ROW_DX, pin_y(11)), "RST", W_SIG, pcbnew.B_Cu)

    # GND: lane C east joins the two mounting tabs under the connector body and the whole lot
    # drops to the ground plane through one via. JP1.3, JP1.4 and JP2.2 pick it up from the
    # plane, so no GND track has to thread past the header columns.
    B.path([
        (FFC_PAD_X[4], pad_y),
        (FFC_PAD_X[4], LANE_C),
        (X_GND, LANE_C),
        (X_GND, Y_TABS, 0.25),
        (MP_TAB_X, Y_TABS, W_PWR),
        (-MP_TAB_X, Y_TABS),
    ], "GND", W_THIN)
    B.track((0.0, Y_TABS), (0.0, Y_TAB_VIA), "GND", W_PWR)
    B.via((0.0, Y_TAB_VIA), "GND", VIA_D_PWR, VIA_DRILL_PWR)


def ground_zone(B):
    zone = pcbnew.ZONE(B.board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(B.net("GND"))
    zone.SetAssignedPriority(0)
    zone.SetLocalClearance(mm(0.30))
    # 0.30 rather than the usual 0.25: at 0.25 the fill squeezes a sliver into one of the gaps
    # between the B.Cu crossings and DRC flags it.
    zone.SetMinThickness(mm(0.30))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    zone.SetThermalReliefGap(mm(0.35))
    zone.SetThermalReliefSpokeWidth(mm(0.50))
    zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)

    # The zone stops short of the notch entirely rather than trying to follow it into the two
    # legs. Nothing on GND lives down there: the pin 12 pads are SCL and RDY.
    pts = pcbnew.VECTOR_VECTOR2I()
    for sx, sy in (
        (BOARD_X0 + ZONE_INSET, NOTCH_Y + ZONE_INSET),
        (BOARD_X1 - ZONE_INSET, NOTCH_Y + ZONE_INSET),
        (BOARD_X1 - ZONE_INSET, BOARD_Y1 - ZONE_INSET),
        (BOARD_X0 + ZONE_INSET, BOARD_Y1 - ZONE_INSET),
    ):
        pts.append(xy(sx, sy))
    zone.AddPolygon(pts)
    B.board.Add(zone)

    # Island removal only works once the filler can see which copper reaches GND, so the
    # connectivity graph has to exist before the fill, not after.
    B.board.BuildConnectivity()
    pcbnew.ZONE_FILLER(B.board).Fill(B.board.Zones())
    B.board.BuildConnectivity()

    islands = zone.GetFilledPolysList(pcbnew.B_Cu).OutlineCount()
    assert islands == 1, \
        "GND zone filled as %d separate pours; an isolated island means some copper is " \
        "not reaching GND" % islands
    print("GND zone filled: %.1f mm2, single pour" % pcbnew.ToMM(pcbnew.ToMM(zone.GetFilledArea())))


def silkscreen(B):
    F, Bk, FAB = pcbnew.F_SilkS, pcbnew.B_SilkS, pcbnew.F_Fab

    # At 20 mm wide there is no margin outboard of the headers, so everything lives either in
    # the strip above CON1 or in the centre channel. Silk over a track is not a DRC problem
    # (tracks are under mask); only silk over a pad's mask opening is.
    B.text("1:SDA SCL VCC GND RST RDY", (0, 22.6), 0.6, F, 0.1)

    B.text("D8>SDA", (-3.2, -10.6), 0.6, F, 0.1)
    B.text("D9>SCL", (-3.2, -12.6), 0.6, F, 0.1)
    B.text("RST<D16", (3.2, -10.6), 0.6, F, 0.1)
    B.text("RDY<D10", (3.2, -12.6), 0.6, F, 0.1)
    B.text("GND", (-3.2, 3.0), 0.6, F, 0.1)
    B.text("VCC", (3.2, 3.0), 0.6, F, 0.1)

    # Pin 1 markers, inboard of the header pads.
    B.text("1", (-4.6, PIN1_Y), 0.8, F, 0.12)
    B.text("1", (4.6, PIN1_Y), 0.8, F, 0.12)

    B.text("TPS43 v1.1", (0, 0.0), 0.8, F, 0.12)
    B.text("TPS43 interp", (0, 0.0), 0.7, Bk, 0.1, mirror=True)
    B.text("v1.1  nano up", (0, -2.0), 0.7, Bk, 0.1, mirror=True)
    B.text("20.0 x 40.0 x 1.0mm  2L FR4  1oz  ENIG", (0, -5.0), 0.6, FAB, 0.1)

    for ref in ("JP1", "JP2"):
        B.strip_silk(ref)
    B.move_field("JP1", "ref", (-4.0, 5.5), 0.8)
    B.move_field("JP2", "ref", (4.0, 5.5), 0.8)
    B.move_field("CON1", "ref", (0.0, 13.4), 0.8)
    B.move_field("R1", "ref", (R1_X, 20.8), 0.6)
    B.move_field("R2", "ref", (0.0, R2_Y), 0.6)
    for ref in ("JP1", "JP2", "CON1", "R1", "R2"):
        B.move_field(ref, "value", (0, 0), 0.8, pcbnew.F_Fab, hide=True)


# --------------------------------------------------------------------------------------------
# Self checks. These exist so that a bad edit fails here instead of producing a board that
# looks plausible and fabricates wrong.
# --------------------------------------------------------------------------------------------


def approx(a, b, tol=0.002):
    return abs(a - b) <= tol


def verify_pinout(B):
    """The routing below is hand-derived for the mirrored cable. Refuse anything else rather
    than emit a board whose routing looks plausible but connects the wrong things."""
    assert CON1_MIRRORED, (
        "gen_schematic.CON1_MIRRORED is False, but route() only implements the mirrored\n"
        "pinout. A straight-through cable flips the escape-lane order, which means:\n"
        "  - the pull-ups move to the east side (SCL and SDA leave on the east lanes)\n"
        "  - RDY and NRST move to the JP1 column and I2C moves to JP2\n"
        "  - the ZMK overlay psels and rdy/rst gpios all change\n"
        "That is a re-layout, not a flag flip. Update route(), the trunk constants and the\n"
        "resistor placement together, then remove this assertion.")

    # Each CON1 pad has to carry the trackpad pin it will actually mate with.
    expected = {n: TPS43_J1[7 - n] for n in range(1, 7)}
    for num, want in expected.items():
        got = B.pad("CON1", num).GetNetname()
        assert got == want, \
            "CON1.%d carries %s but mates with TPS43 J1.%d (%s)" % (num, got, 7 - num, want)
    print("CON1 pinout OK (mirrored: CON1.N mates TPS43 J1.%s)" % "7-N")


def verify_footprint_geometry(B):
    """The routing constants above are hand-derived from the library footprints. If a library
    update moves a pad, the lanes silently stop lining up, so pin them down here."""
    for num, want_x in FFC_PAD_X.items():
        gx, gy = B.pad_spec_pos("CON1", num)
        assert approx(gx, want_x), "CON1.%d X %.4f expected %.4f" % (num, gx, want_x)
        assert approx(gy, FFC_PAD_Y), "CON1.%d Y %.4f expected %.4f" % (num, gy, FFC_PAD_Y)

    for ref, cy in (("R1", R1_Y), ("R2", R2_Y)):
        p1y = B.pad_spec_pos(ref, 1)[1]
        p2y = B.pad_spec_pos(ref, 2)[1]
        assert approx(p1y, cy + 0.9125) and approx(p2y, cy - 0.9125), \
            "%s rotated wrong: pad1 y=%.4f pad2 y=%.4f" % (ref, p1y, p2y)
        assert p1y > p2y, "%s pad 1 must be the north (VCC) pad" % ref
    # The stub constants have to track the resistor placement.
    assert approx(Y_SDA_STUB, R1_Y - 0.9125) and approx(Y_SCL_STUB, R2_Y - 0.9125), \
        "pull-up stub Y constants are out of sync with the resistor placement"

    for ref, x in (("JP1", -ROW_DX), ("JP2", ROW_DX)):
        for n in (1, 12):
            gx, gy = B.pad_spec_pos(ref, n)
            assert approx(gx, x) and approx(gy, pin_y(n)), \
                "%s.%d at (%.4f, %.4f)" % (ref, n, gx, gy)

    # The escape corridor only exists if the MP tabs really are where we think.
    mp_north = max(
        PAGE_Y - pcbnew.ToMM(p.GetPosition().y) + pcbnew.ToMM(p.GetSize().y) / 2.0
        for p in B.pads("CON1", "MP"))
    pad_south = FFC_PAD_Y - 1.3 / 2.0
    assert approx(mp_north, 18.85, 0.01), "MP tab north edge %.4f" % mp_north
    for lane in (LANE_A, LANE_B, LANE_C):
        assert mp_north + 0.2 < lane - W_THIN / 2, "lane %.3f too close to MP tabs" % lane
        assert lane + W_THIN / 2 < pad_south - 0.19, "lane %.3f too close to pads" % lane
    print("footprint geometry OK (corridor %.3f mm, lanes %.3f/%.3f/%.3f)"
          % (pad_south - mp_north, LANE_C, LANE_B, LANE_A))


def bbox_mm(item):
    bb = item.GetBoundingBox()
    return (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
            pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))


def verify_clearances(B):
    """Cheap sanity checks. kicad-cli pcb drc is the real gate; these just catch the
    mistakes that are easy to make while editing coordinates."""
    board = B.board

    # 1. Courtyards must not overlap.
    fps = list(board.GetFootprints())
    for i, a in enumerate(fps):
        for b in fps[i + 1:]:
            ca, cb = a.GetCourtyard(pcbnew.F_CrtYd), b.GetCourtyard(pcbnew.F_CrtYd)
            if ca.OutlineCount() == 0 or cb.OutlineCount() == 0:
                continue
            al, at, ar, ab = bbox_mm(a)
            bl, bt, br, bb_ = bbox_mm(b)
            if not (ar < bl or br < al or ab < bt or bb_ < at):
                # bounding boxes touch, do the real test
                test = pcbnew.SHAPE_POLY_SET(ca)
                test.BooleanIntersection(cb)
                assert test.OutlineCount() == 0, \
                    "courtyards of %s and %s overlap" % (a.GetReference(), b.GetReference())

    # 2. Everything copper stays inside the board with edge clearance to spare.
    lim = 0.40
    for t in board.GetTracks():
        l, top, r, bot = bbox_mm(t)
        sx0, sx1 = l - PAGE_X, r - PAGE_X
        sy1, sy0 = PAGE_Y - top, PAGE_Y - bot
        assert BOARD_X0 + lim <= sx0 and sx1 <= BOARD_X1 - lim, \
            "track outside board in X: %.3f..%.3f" % (sx0, sx1)
        assert BOARD_Y0 + lim <= sy0 and sy1 <= BOARD_Y1 - lim, \
            "track outside board in Y: %.3f..%.3f" % (sy0, sy1)

    # 3. Every net that should exist has at least two pads on it.
    for name in ("GND", "VCC", "SDA", "SCL", "RDY", "RST"):
        code = B.net(name).GetNetCode()
        pads = [p for fp in fps for p in fp.Pads() if p.GetNetCode() == code]
        assert len(pads) >= 2, "net %s only reaches %d pad(s)" % (name, len(pads))

    print("self checks OK")


if __name__ == "__main__":
    build()
