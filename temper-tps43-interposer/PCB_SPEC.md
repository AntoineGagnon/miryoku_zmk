# Temper TPS43 Interposer, as-built PCB specification

This describes the board that `gen_interposer.py` and `gen_schematic.py` actually produce. It is
documentation, not input: the generators are the source of truth. If a number here disagrees with
the generator, the generator is right and this file is stale.

Section 11 lists the deviations from the original hand-written specification and why each one was
necessary.

## Purpose

A thin (1.0 mm) interposer that sits between a nice!nano v2 (nRF52840) and the Temper keyboard
PCB. It passes through all 24 Pro Micro pins while tapping four unused GPIOs plus VCC and GND to
a 6-pin 0.5 mm FFC connector for an Azoteq TPS43 trackpad. Two 0805 pull-up resistors sit on the
I2C bus.

---

## 1. Mechanical

| Parameter | Value |
|-----------|-------|
| Width | 20.0 mm |
| Height | 40.0 mm (notched south edge) |
| Thickness | 1.0 mm |
| Layers | 2 (F.Cu + B.Cu) |
| Substrate | FR-4, 1 oz copper |
| Surface finish | ENIG (recommended for the 0.5 mm FFC pads) |
| Outline | rectangle with a notched south edge (see below) |

### Coordinate frame

All coordinates below are in the **spec frame**: X is centred on the board and +Y points toward
the trackpad (up, when looking at the front of the board). Board extents are therefore:

| Axis | Range |
|---|---|
| X | -10.00 to +10.00 |
| Y | -16.50 to +23.50 |

The frame origin is **not** the geometric centre of the board; the centre is at Y = +1.50. The
origin is on the header pin grid instead, which is what makes the pin coordinates come out round.
KiCad's own Y axis points down, so `gen_interposer.py` converts once, in `xy()`, and every
constant in the file is spec-frame. The board's auxiliary and grid origins are both set to spec
(0, 0).

### Placement

| Ref | Footprint | Library | Position | Rotation |
|-----|-----------|---------|----------|----------|
| JP1 | `PinHeader_1x12_P2.54mm_Vertical` | `Connector_PinHeader_2.54mm` | pin 1 at (-7.62, +12.70) | 0 |
| JP2 | `PinHeader_1x12_P2.54mm_Vertical` | `Connector_PinHeader_2.54mm` | pin 1 at (+7.62, +12.70) | 0 |
| CON1 | `Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal` | `Connector_FFC-FPC` | (0, +19.15) | 0 |
| R1 | `R_0805_2012Metric` | `Resistor_SMD` | (-8.50, +16.60) | 270 |
| R2 | `R_0805_2012Metric` | `Resistor_SMD` | (+2.50, +7.00) | 270 |

The pull-ups end up on opposite sides, which looks arbitrary but is forced. The escape corridor
makes SDA the outermost west trunk, so SDA is fenced west of SCL for its whole length and no
single spot reaches both on F.Cu. R1 goes west of the JP1 pad column, where SDA reaches it over
the top of the header pads; R2 goes in the centre channel, where SCL reaches it without crossing
anything. Both VCC pads are fed from B.Cu. R2 therefore sits under the nice!nano; with Mill-Max
sockets that is about 2 mm of clearance over a 0.5 mm part.

Headers carry `exclude_from_pos_files` (hand-soldered) but stay in the BOM. CON1, R1 and R2 are
`smd`. All five footprints come from the stock KiCad 10 libraries; the project contains no custom
footprint library.

The pin header footprint's origin is **pin 1**, not its geometric centre, and its pins run along
local +Y, which maps to spec -Y at rotation 0. Placing the origin at pin 1 is therefore all that
is required; pin 12 lands at Y -15.24 on its own. Row spacing is 15.24 mm and pitch is 2.54 mm.

R1 and R2 are rotated 270 so that **pad 1 is the north (VCC) end** and pad 2 the south (signal)
end. That matches how the schematic draws them, pull-up to the rail at the top.

### Vertical budget

Every clearance in the crowded northern half of the board:

```
Y +23.50   board top edge
Y +23.10   copper-to-edge limit (0.40 mm)
Y +22.15   CON1 courtyard north            1.35 mm to the board edge
Y +21.65   CON1 signal pad north ends
Y +21.00   CON1 signal pad centres         0.30 x 1.30 mm pads on 0.50 mm pitch
Y +20.35   CON1 signal pad south ends   ─┐
Y +20.025  escape lane A                 │  1.50 mm corridor
Y +19.600  escape lane B                 │  three 0.20 mm tracks, 0.225 mm gaps
Y +19.175  escape lane C                 │
Y +18.85   CON1 mounting tab north      ─┘
Y +16.60   R1 centre                       (X -8.50, west of the JP1 column)
Y +16.65   CON1 mounting tab south
Y +14.25   CON1 courtyard south            0.45 mm to the header courtyards
Y +13.80   JP1 / JP2 courtyard north
Y +13.55   JP1 / JP2 pad 1 north edge
Y +12.70   header pin 1
```

Courtyard extents: CON1 X -4.55 to +4.55; R1 X -9.45 to -7.55 (Y 14.92 to 18.28); R2 X +1.55 to
+3.45 (Y 5.32 to 8.68); JP1 X -8.72 to -6.52 (Y <= 13.80). Nothing overlaps, and
`gen_interposer.py` asserts it before saving.

### The notched south edge

Temper's nice!view header J2 spans X 171.63..184.48, Y 86.33..92.16, which in this frame starts
at Y -15.21, level with header pin 12. Any board reaching pin 12 overlaps it. The south edge is
therefore full width down to Y -15.20 and then splits into two legs at |X| 6.35..10.00 running to
Y -16.50. The legs carry the pin 12 pads (pad edge at |X| 6.77, so 0.42 mm of edge clearance) and
sit outside J2's width, which ends at |X| 6.43.

---

## 2. Pin mapping

### JP1, left row (viewed from the top of the board, USB pointing away)

| Pin | Pro Micro | nRF52840 | Net |
|-----|-----------|----------|-----|
| 1 | D1 / TX | P0.06 | pass-through |
| 2 | D0 / RX | P0.03 | pass-through |
| 3 | GND | - | **GND** |
| 4 | GND | - | **GND** |
| 5 | D2 | P0.17 | pass-through (nice!view) |
| 6 | D3 | P0.20 | pass-through (nice!view) |
| 7 | D4 / A6 | P0.04 | pass-through |
| 8 | D5 | P0.05 | pass-through |
| 9 | D6 / A7 | P0.07 | pass-through |
| 10 | D7 | P0.08 | pass-through |
| 11 | **D8 / A8** | **P1.04** | **SDA** |
| 12 | **D9 / A9** | **P1.06** | **SCL** |

### JP2, right row

| Pin | Pro Micro | nRF52840 | Net |
|-----|-----------|----------|-----|
| 1 | RAW | - | pass-through |
| 2 | GND | - | **GND** |
| 3 | RST | P0.18 | pass-through |
| 4 | **VCC** | 3.3 V | **VCC** |
| 5 | D21 / A3 | P0.30 | pass-through |
| 6 | D20 / A2 | P0.28 | pass-through |
| 7 | D19 / A1 | P0.31 | pass-through |
| 8 | D18 / A0 | P0.29 | pass-through |
| 9 | D15 / SCK | P0.02 | pass-through |
| 10 | D14 / MISO | - | pass-through |
| 11 | **D16 / MOSI** | **P0.10** | **RST** (trackpad reset) |
| 12 | **D10 / A10** | **P0.09** | **RDY** |

"Pass-through" means a plated through-hole with **no copper attached anywhere on either layer**.
The schematic marks these pins no-connect, so KiCad gives each one an auto-generated
`unconnected-(JP1-Pin_1-Pad1)`-style net. That is deliberate: it is exactly what "Update PCB from
Schematic" would produce, and it is what lets `--schematic-parity` come out clean.

### CON1 pinout

CON1 pin 1 is at X -1.25 (west) and pin 6 at X +1.25 (east), all at Y +21.00 on 0.50 mm pitch.

**CON1 is the mirror of the trackpad's own connector.** The Azoteq TPS43's J1 pinout is
`1:RDY 2:NRST 3:GND 4:VDDHI 5:SCL 6:SDA` (*ProxSense Standard Trackpad Module* datasheet,
revision 1.06, August 2025), and this board is built for an FFC cable that reverses the conductor
order end to end, so CON1 pin N mates with TPS43 J1 pin 7−N.

| Pin | Net | Mates with | Also connects to |
|-----|-----|-----------|------------------|
| 1 | SDA | TPS43 J1.6 SDA | JP1.11, R1 pad 2 |
| 2 | SCL | TPS43 J1.5 SCL | JP1.12, R2 pad 2 |
| 3 | VCC | TPS43 J1.4 VDDHI | JP2.4, R1 pad 1, R2 pad 1 |
| 4 | GND | TPS43 J1.3 GND | ground plane, mounting tabs |
| 5 | RST | TPS43 J1.2 NRST | JP2.11 |
| 6 | RDY | TPS43 J1.1 RDY | JP2.12 |
| MP (x2) | GND | - | ground plane |

This mapping lives in `gen_schematic.py` as `TPS43_J1` plus a `CON1_MIRRORED` flag, and
`verify_pinout()` in `gen_interposer.py` asserts that every CON1 pad carries the net its mating
TPS43 pin expects. It also refuses to build the straight-through variant, because that flips the
escape-lane order and therefore requires re-laying out the pull-ups and re-assigning the header
pins; see section 11.

Do not take the TPS43 pinout from the 2016 revision 1.02 PDF still mirrored on distributor sites.
Revision 1.04 (December 2022) is recorded as "Update Figure 2-1 and Table 2-1", and Table 2-1 is
exactly this table: the old copy has SDA and NRST swapped.

### Resistors

| Ref | Value | Pad 1 (north) | Pad 2 (south) |
|-----|-------|---------------|---------------|
| R1 | 2.2 kOhm | VCC | SDA |
| R2 | 2.2 kOhm | VCC | SCL |

---

## 3. Net list

| Net | Members |
|-----|---------|
| GND | JP1.3, JP1.4, JP2.2, CON1.4, CON1.MP x2, B.Cu zone |
| VCC | JP2.4, CON1.3, R1.1, R2.1 |
| SDA | JP1.11, CON1.1, R1.2 |
| SCL | JP1.12, CON1.2, R2.2 |
| RDY | JP2.12, CON1.6 |
| RST | JP2.11, CON1.5 |
| `unconnected-(...)` x16 | one per pass-through header pin, no copper |

35 pads across 22 nets. `gen_schematic.netlist()` is the single definition of this table;
`gen_interposer.py` imports it, so the board and the schematic cannot disagree.

---

## 4. Routing

### Design rules

| Constraint | Value |
|-----------|-------|
| Minimum track width | 0.20 mm |
| Minimum clearance | 0.20 mm |
| Minimum via | 0.60 mm pad / 0.30 mm drill |
| Minimum hole | 0.30 mm |
| Minimum via annular ring | 0.13 mm |
| Copper to board edge | 0.40 mm |
| Silkscreen clearance | 0.15 mm |
| Minimum connection width | 0.20 mm |
| Courtyard overlap | error |

Track widths used: 0.20 mm for signals and for everything inside the escape corridor, 0.50 mm for
VCC and GND once clear of it. Vias: 0.60/0.30 mm for SCL, 0.80/0.40 mm for VCC and GND.

### Connector escape

The six FFC pads all escape **south**, through the 1.50 mm corridor between the pad row
(south edge Y +20.35) and the mounting tabs (north edge Y +18.85). Three lanes go west and three
east, at 0.20 mm width with 0.225 mm gaps everywhere:

| Lane | Y | West | East |
|------|---|------|------|
| A | 20.025 | CON1.1 SDA | CON1.6 RDY |
| B | 19.600 | CON1.2 SCL | CON1.5 RST |
| C | 19.175 | CON1.3 VCC | CON1.4 GND |

Each pad drops straight south from its centre to its own lane, then turns outward. Because the
inner pads own the lower lanes and turn later, no two tracks cross.

**Each lane then holds its Y until it reaches its own trunk X and turns square.** Do not
"optimise" this into a diagonal shortcut: a lane that dives toward its trunk cuts the corner off
the lane below it, and at 0.425 mm lane spacing that lands at 0.145 mm, below the 0.20 mm
minimum. The first version of this board did exactly that and DRC caught it.

The lane assignment is forced, not chosen. The pad nearest the board centre must take the
innermost lane so it can duck under its neighbours' drops. A lane turning south then blocks every
lane below it from reaching further out, so lane A turns furthest from the centre and lane C
nearest to it, and whichever net lands on lane C is boxed in. Here that is VCC (west) and GND
(east), which is workable: GND only needs the plane, and VCC has to cross the board anyway.

Trunk X values, outward to inward: SDA -6.35, SCL -5.75, VCC -5.15, GND +5.15, RST +5.75,
RDY +6.35. At 20 mm wide there is no room outside the header columns, so all six run in the
2.22 mm band between the header pads (|X| 6.77) and the mounting tabs (|X| 4.05), on 0.60 mm
centres.

### Nets, end to end

| Net | Path |
|-----|------|
| SDA | CON1.1 -> lane A -> south at X -6.35 -> west into JP1.11. F.Cu stub west at Y +15.69 to R1 pad 2, crossing above the header pads with 2.1 mm to spare. |
| SCL | CON1.2 -> lane B -> south at X -5.75 -> west at Y -14.00 to the header column -> down into JP1.12. F.Cu stub east at Y +6.09 to R2 pad 2. |
| VCC | CON1.3 -> lane C -> south at X -5.15 -> east to the hub at (-3.00, 13.00) -> via to B.Cu. B.Cu chains hub -> R2 tap (2.50, 10.00) -> JP2.4, with a second spur hub -> R1 tap (-8.50, 19.00). Each tap vias back up to its resistor's VCC pad. |
| GND | CON1.4 -> lane C -> south at X +5.15 -> west at Y +17.75 onto both mounting tabs -> via at (0, 15.00) to the plane. JP1.3, JP1.4 and JP2.2 join through the plane. |
| RST | CON1.5 -> lane B -> south at X +5.75 -> via at (+5.75, -12.70) to B.Cu -> east into JP2.11. |
| RDY | CON1.6 -> lane A -> south at X +6.35 -> east at Y -14.00 -> down into JP2.12. |

SCL and RDY cross to the header column at Y -14.00 rather than running straight down to pin 12:
below Y -15.20 the notch means there is no board at their trunk X.

Five vias, and each earns its place:

- **VCC** (3 vias). Lane C is boxed in between the SCL trunk and the connector's west mounting
  tab and cannot travel on F.Cu at all, so it drops to B.Cu. B.Cu also has to carry it to JP2.4,
  since VCC exists only on JP2 (east), and back up to each pull-up. The original spec's claim
  that F.Cu-only routing with no vias was achievable is simply wrong for this net list.
  The B.Cu spurs are chained rather than fanned: two spurs leaving the hub 8 degrees apart pinch
  a thin wedge of zone between them, which DRC reports as a copper sliver.
- **RST** (1 via). RDY holds the outer east trunk, so it must serve the more southern header pin,
  otherwise the inner trunk's jog cuts across it. Without this via, RDY and RST would swap header
  pins and the ZMK overlay would change.
- **CON1's mounting tabs** (1 via) reach the ground plane, picking up the GND escape lane on the


### Ground plane

A single GND zone on B.Cu, inset 0.50 mm from the board outline, filling 1289 mm2 as one pour.
Clearance 0.30 mm, minimum thickness 0.25 mm, thermal reliefs on through-hole pads with 0.35 mm
gap and 0.50 mm spokes, isolated islands removed. F.Cu has no pour, which keeps copper away from
the fine-pitch FFC pads.

`gen_interposer.py` builds connectivity **before** filling and then asserts the result is a
single outline. Filling without connectivity produces a stray isolated island that KiCad's own
refill would silently delete, so the shipped fill would not match a freshly-filled one.

---

## 5. Layers

| Layer | Content |
|-------|---------|
| F.Cu | all signal routing, SMD pads for CON1/R1/R2, through-hole pads |
| B.Cu | GND plane, the VCC and SCL crossings, through-hole pads |
| F.Mask / B.Mask | solder mask |
| F.Paste / B.Paste | paste for the three SMD parts |
| F.SilkS | designators, pin labels, connector legend, title |
| B.SilkS | "Bottom: Temper" |
| F.Fab | board spec note |
| F.CrtYd / B.CrtYd | courtyards, checked by DRC |
| Edge.Cuts | 34 x 44 mm rectangle |

---

## 6. Footprints

No custom footprint library. All five footprints are stock KiCad 10:

| Ref | Library : footprint |
|-----|---------------------|
| JP1, JP2 | `Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical` |
| CON1 | `Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal` |
| R1, R2 | `Resistor_SMD:R_0805_2012Metric` |

The project's `fp-lib-table` points at these through `${KICAD10_FOOTPRINT_DIR}`.
`gen_interposer.py` restores the library nickname on each loaded footprint with `SetFPID()`;
`FootprintLoad()` returns a bare name, and without the nickname DRC reports every footprint as
mismatched against the schematic.

### CON1 orientation

The FH12's signal pads sit at footprint-local -Y, which is spec **+Y** at rotation 0. So the pads
and the cable opening both face the top edge of the board: the cable runs straight out to the
trackpad with no fold, and never passes under the nice!nano. The slide-lock actuator and the
mounting tabs are on the south side, facing the headers, with 0.45 mm of courtyard clearance for
actuator travel.

The escape corridor runs underneath the connector's nose, between the signal pads and the
mounting tabs. This is the connector's normal land-pattern free area: the housing is plastic, the
tracks are under solder mask, and the FH12 has no locating bosses.

Because the pads face +Y and pin 1 is at local -X, **pin 1 lands on the west side**. That is what
fixes VCC as the westmost pad and forces its B.Cu crossing. Reorienting the connector cannot fix
that: mirroring the pad order would require putting the part on B.Cu.

### Footprint geometry is asserted, not assumed

`verify_footprint_geometry()` re-derives every routing-critical dimension from the loaded
footprints and asserts it: the six FFC pad positions, the mounting tab north edge, the resistor
pad polarity, the header pin 1 and 12 positions, and that all three lanes clear both the pads
above and the tabs below. A library update that nudges a pad fails the build instead of silently
producing a shorted board.

---

## 7. Silkscreen

| Text | Position | Size | Layer |
|------|----------|------|-------|
| `1:SDA 2:SCL 3:VCC 4:GND 5:RST 6:RDY` | (0, +22.4) | 0.7 | F.SilkS |
| `GND` | (-11.2, +7.62) | 0.7 | F.SilkS |
| `VCC` | (+10.4, +5.08) | 0.7 | F.SilkS |
| `D8` / `D9` | (-11.2, -12.70) / (-11.2, -15.24) | 0.7 | F.SilkS |
| `D16` / `D10` | (+10.4, -12.70) / (+10.4, -15.24) | 0.7 | F.SilkS |
| `1` (pin 1 markers) | (-10.6, +12.70) and (+9.9, +12.70) | 0.8 | F.SilkS |
| `Temper TPS43 Interposer` | (0, -18.1) | 1.0 | F.SilkS |
| `v1.0   Top: nice!nano` | (0, -19.6) | 0.7 | F.SilkS |
| `Bottom: Temper` | (0, -18.1) | 1.0 | B.SilkS, mirrored |
| `34.0 x 44.0 x 1.0mm   2L FR4   1oz   ENIG` | (0, -16.0) | 0.6 | F.Fab |

Designators: JP1 at (-14.2, 0), JP2 at (+14.2, 0), CON1 at (0, +13.4), R1 at (-12.00, +21.4),
R2 at (-14.50, +21.4). Value fields are hidden on F.Fab. The header designators sit outboard of
both the pin-function labels and the SDA trunk; an earlier position at X -6.0 put JP1's text on
JP1's own pad 6.

The title sits in the strip below the headers because it is the only free band left; the header
silkscreen runs down to Y -16.62 and the board edge is at -20.50. CON1's designator is at
Y +13.4 rather than +14.0 for the same reason: at +14.0 it clipped CON1's own silk outline by
0.13 mm.

---

## 8. Bill of materials

See `BOM.md`.

---

## 9. Assembly

The nice!nano ends up on **top** of the interposer, so:

1. **Top side:** 24 **Mill-Max 310 series machine sockets** at JP1 and JP2, to receive the
   Mill-Max pins already soldered to the nice!nano.
2. **Bottom side:** 24 **Mill-Max pins**, pointing down, to plug into Temper's own sockets.
   Not 2.54 mm square breakaway header pins: Temper uses Mill-Max 310 sockets, whose bore takes
   ~0.5 mm round pins. A 0.64 mm square pin does not fit and destroys the socket. The 1.0 mm
   holes in this footprint suit both parts.
3. **Top side:** CON1. Both mounting tabs must be soldered; they are its only retention.
4. **Top side:** R1 and R2.
5. Unplug the nice!nano from Temper, plug the interposer into Temper, plug the nice!nano into the
   interposer.
6. Connect the TPS43 with a 6-pos 0.5 mm FFC cable. **Ring the cable out first**, see below.

### The cable must be verified before fabbing

CON1 is wired for a cable that reverses the conductor order, so CON1 pin N reaches TPS43 J1
pin 7−N. A straight-through cable scrambles every signal and puts 3.3 V on the trackpad's RDY pin.

Ignore the Type A / Type B label: the naming is not standardised. DigiKey and Molex call same-side
contacts Type A and opposite-side Type D; other vendors call the same thing Type B, Type 1 or
Type 2. FH12-6S-0.5SH is bottom-contact, so at the interposer end the conductors face the board,
but that alone does not fix the mapping.

Lay the cable out as it will actually run and check continuity from conductor 1 at one end:

- reaches conductor **6** at the other end: reversed, this board is correct
- reaches conductor **1**: straight-through, this board is wrong and needs the re-layout in
  section 11

Open mechanical risk: CON1 spans Y +14.25 to +22.15, in front of the nice!nano's USB-C port.
The module is lifted 4 to 8.5 mm by the sockets and the FH12 is about 2 mm tall, so it should
clear, but measure it against the actual sockets before ordering.

---

## 10. ZMK firmware

Unchanged from the original design. See the ZMK section of `README.md` for the full overlay.
I2C1 on P1.04 (SDA, D8) and P1.06 (SCL, D9), a separate bus from `&pro_micro_i2c` because the
default pins D2/D3 are taken by the nice!view display's SPI. RDY on `&pro_micro 10`, trackpad
reset on `&pro_micro 16`.

`CONFIG_INPUT_TPS43=y`, `CONFIG_I2C=y`, `CONFIG_ZMK_POINTING=y`. Driver module:
`stelmakhdigital/zmk_driver_azoteq`. `CONFIG_NFCT_PINS_AS_GPIOS=y` is REQUIRED: RDY is on
D10 = P0.09 and the trackpad reset on D16 = P0.10, which are the nRF52840's NFC antenna pins.

---

## 10a. Verified against the Temper hardware

Measured from `raeedcho/temper` (`pcb/temper.kicad_pcb`, `pcb/temper.kicad_sch`) and the shield
at `raeedcho/temper-zmk-config`, rather than taken on trust from the original spec.

### Pin availability, confirmed

Temper's exported netlist marks D0, **D8**, **D9**, **D10**, D14 and **D16** as unconnected.
Used: D1 (nice!view CS), D2 (MOSI), D3 (SCK), D4-D7 (matrix rows), D15/D18/D19/D20/D21 (columns),
plus RESET, VCC, three GNDs and BATTERY+. The four pins this interposer taps are genuinely free.

Note the display is a **nice!view on SPI** at the PCB level (CS/MOSI/SCK on D1/D2/D3). The
miryoku outboard shield's `temper.dtsi` instead declares an SSD1306 OLED on `&pro_micro_i2c`,
which is D2/D3. Either way D1, D2 and D3 are taken, so the trackpad needs its own I2C bus.

### Geometry, which set the board size

| Feature | Position on Temper | Effect |
|---|---|---|
| Controller header columns | X 170.43 and 185.67 | interposer centres on X 178.05 |
| Choc sockets SW5/SW10/SW15 | X 148.34..167.49, gap 1.60 mm | caps half-width at ~10.06 mm |
| Board right edge | X 188.29 | 10.0 mm also stays on the board |
| nice!view header J2 | X 171.63..184.48, Y 86.33..92.16 | forces the notched south edge |
| Battery pads BT1 | X 173.62..182.83, Y 57.82..63.08 | sit **under** the nice!nano |
| U1 to board top edge | 10.59 mm of free board | room for CON1 and the cable exit |

The 34 x 44 mm first revision would have sat 6.44 mm over the adjacent switch column, against
choc switches ~4.7 mm tall, and overhung the right board edge by 6.76 mm. It was unbuildable.

### Open mechanical risks

- **Battery wiring.** Temper's assembly guide has you solder battery wires to BT1, directly under
  the nice!nano. The interposer's B.Cu ground pour ends up over that wiring with only the socket
  standoff between. Dress the wires flat and check for chafing.
- **USB-C.** CON1 spans Y +14.25..+22.15, in front of the nice!nano's USB port. Mill-Max sockets
  lift the module only ~2 mm, so this is tighter than with tall sockets. Measure it.
- **nice!view.** Even with the notch, the two legs pass alongside J2. Check clearance against an
  actual nice!view before committing.
- **Handedness.** Temper is a reversible PCB. This interposer is only correct for the orientation
  where JP1 lands on the column carrying D8/D9. On the mirrored half it would land on the other
  column. The outline and CON1 are symmetric about X, so a mirrored variant needs only the
  routing regenerated, but it is not the same board.

---

## 11. Deviations from the original specification

The original hand-written spec contained several errors that made it unbuildable as written.

### The FFC pinout, which was the serious one

The original spec's CON1 pinout was `1:VDD 2:SDA 3:SCL 4:RDY 5:RST 6:GND`. The Azoteq TPS43's
actual J1 pinout is `1:RDY 2:NRST 3:GND 4:VDDHI 5:SCL 6:SDA` (datasheet revision 1.06, August
2025). The spec's order is neither that nor its reversal, so **no cable orientation could have
made it work**. Built as specified with a straight-through cable it would have produced:

| CON1 pin | Spec net | Lands on TPS43 | Result |
|---|---|---|---|
| 1 | VDD 3.3 V | RDY | 3.3 V driven onto the trackpad's interrupt output |
| 2 | SDA | NRST | trackpad held in whatever state the bus idles at |
| 3 | SCL | GND | I2C clock shorted to ground, bus dead |
| 4 | RDY | VDDHI | trackpad powered from a GPIO |
| 5 | RST | SCL | - |
| 6 | GND | SDA | I2C data shorted to ground |

Part of the explanation: the pinout changed. The 2016 revision 1.02 PDF still mirrored on
distributor sites lists TPS43 as `RDY, SDA, GND, VDDHI, SCL, NRST`, and the revision history
records v1.04 (December 2022) as "Update Figure 2-1 and Table 2-1", which is that table. But the
spec's order does not match the old table either, so it appears to have been invented rather than
read off anything.

CON1 is now derived from `TPS43_J1` in `gen_schematic.py` and checked by `verify_pinout()`.

### Everything else

| Original | Problem | Resolution |
|----------|---------|------------|
| R1 at (-3.62, +20.70) and R2 at (-3.62, +18.20), rotated 90 | `R_0805_2012Metric` has a 3.36 x 1.9 mm courtyard, so rotated it needs at least 3.4 mm of Y clearance. At 2.5 mm spacing the two collide, and R2 also overlaps CON1's courtyard. | Moved to (-12.00, +18.00) and (-14.50, +18.00), rotated 270, west of the JP1 pad column where the SDA trunk can reach them. |
| "All routing on F.Cu only", "No vias required" | Geometrically impossible for any realistic pinout. The connector's innermost escape lane is boxed in and cannot travel on F.Cu at all, and VCC exists only on JP2 (east) so it always has to cross the centre channel. | Six vias, on B.Cu. Documented per net in section 4. |
| Custom `TPS43_FFC_06` footprint for Molex 503480-0600, with 0.70 mm non-plated mounting holes | The real Molex part has SMT solder tabs, not holes. As drawn, the connector had zero mechanical retention, and the pad geometry was never checked against any datasheet. | Dropped the custom library entirely. CON1 is now the stock, datasheet-derived Hirose FH12-6S-0.5SH footprint with two SMT solder tabs. |
| §9.1/9.2: male pins on top, female sockets on bottom | Contradicts §9.5 of the same document and is backwards for an interposer. Sockets on the bottom cannot mate with Temper's sockets. | Female sockets on top (receive the nice!nano), male pins on the bottom (plug into Temper). |
| §1 "(0, 0) at the geometric centre" | Contradicts the stated extents of -20.50 to +23.50, whose centre is +1.50. | Kept the spec's component coordinate frame, which all its other numbers assume, and documented that the origin is on the pin grid rather than the centre. |
| §1 "Rotation 0 (cable exits toward +Y)" vs §6 "connector opening faces -Y" | The two sections contradict each other. | Opening faces +Y. The cable runs straight to the trackpad without folding and stays clear of the nice!nano. |
| Silkscreen: title at (0, +22.0), "v1.0" at (0, +20.7), CON1 at (0, +17.7) | That whole region is now occupied by the connector, the escape routing and the resistors. The original positions also put the title through JP1's silk outline. | Title and revision moved to the free strip below the headers; the connector legend is a single line above CON1. |
| §2 JP2 pin 10 "P0.03 or P0.28?" | Unresolved in the original. | Left unresolved and irrelevant: the pin is a pass-through with no copper attached. |
| §5: net 0 for unconnected pads | Correct for a board with no schematic, but it makes `--schematic-parity` report every pass-through pin as a mismatch. | Pass-through pins carry KiCad's own auto-generated `unconnected-(...)` net names, matching what "Update PCB from Schematic" produces. Still no copper attached. |
| CON1 mounting tabs unconnected | Left floating in the original. Two same-named pads on one net that DRC then wants connected to each other. | Tied together and grounded through one via, which is the conventional treatment and gives the shell a return path. |
| §2 nRF52840 numbers for D9, D10, D16 (P0.09 / P0.11 / P1.06) | All three wrong. D9 is P1.06, D10 is P0.09, D16 is P0.10. The overlay's `NRF_PSEL(TWIM_SCL, 0, 9)` put the I2C clock on D10, which this board wires to RDY, so the bus could never have come up. P0.11 is actually D7, one of Temper's matrix rows. | Corrected against ZMK's `arduino_pro_micro_pins.dtsi` and Temper's own schematic. SCL is now `NRF_PSEL(TWIM_SCL, 1, 6)`. |
| §10: NFC config described as optional | RDY (D10 = P0.09) and trackpad reset (D16 = P0.10) are both nRF52840 NFC antenna pins. | `CONFIG_NFCT_PINS_AS_GPIOS=y` is documented as required. |
| BOM: male/female 2.54 mm headers | Temper uses Mill-Max 310 machine sockets, which square header pins do not fit. | Mill-Max pins on the bottom, Mill-Max 310 sockets on top. |
| BOM: "6-pos 0.5mm FFC Type A cable" | The Type A / Type B / Type D / Type 1 / Type 2 naming is not standardised across vendors, so this does not specify anything. | The requirement is stated as the conductor mapping (CON1 pin N to TPS43 pin 7-N) with a continuity check to confirm it, rather than a vendor letter. |
