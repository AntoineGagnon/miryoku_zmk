# Temper TPS43 Interposer PCB

A 1.0 mm interposer that sits between the nice!nano v2 and the Temper keyboard PCB. All 24
Pro Micro pins pass straight through; four unused GPIOs plus VCC and GND are tapped out to a
6-pin 0.5 mm FFC connector for an Azoteq TPS43 trackpad. Two 0805 resistors pull up the I2C bus.

- **Board:** 20.0 x 40.0 x 1.0 mm, 2 layers, FR-4, 1 oz copper, ENIG, notched south edge
- **Toolchain:** KiCad 10
- **Status:** DRC clean, ERC clean, schematic and board verified in parity, gerbers exported

The outline is dictated by the Temper PCB, measured from `raeedcho/temper`:

| Constraint | Measurement | Consequence |
| --- | --- | --- |
| Controller header columns | X 170.43 and 185.67 | interposer centres on X 178.05 |
| Nearest choc hotswap sockets | end at X 167.49, 1.60 mm from the MCU | half-width capped at ~10.06 mm |
| Temper's right board edge | X 188.29 | 10.0 mm also stays on the board |
| nice!view header J2 | X 171.63..184.48, Y 86.33..92.16 | south edge notched to clear it |

An earlier 34 x 44 mm revision would have sat 6.4 mm over the adjacent switch column, against
choc switches that stand ~4.7 mm tall. It could not have been assembled.

## Building it

Everything is generated. Do not hand-edit `.kicad_pcb` or `.kicad_sch`: change the generator
and re-run, otherwise the next build silently throws your edits away.

```sh
./build.sh          # generate, upgrade, ERC, DRC with schematic parity
./build.sh fab      # the above plus gerbers, drill, placement, renders, and a fab zip
```

| File | Role |
| --- | --- |
| `gen_interposer.py` | Emits `temper-tps43-interposer.kicad_pcb` via the KiCad `pcbnew` Python API. Placement, routing, ground plane, silkscreen and the design rules all live here. |
| `gen_schematic.py` | Emits `temper-tps43-interposer.kicad_sch`, and owns the `COMPONENTS` table that is the single source of truth for the netlist. `gen_interposer.py` imports it, so the board and the schematic cannot drift. |
| `build.sh` | Runs both, then gates on ERC, DRC and schematic parity. |
| `PCB_SPEC.md` | The as-built design description. |

`gen_interposer.py` needs KiCad's bundled interpreter (`pcbnew` is not importable from a system
python); `build.sh` finds it. `gen_schematic.py` is plain python3.

## Pin mapping

| Pro Micro | Header pin | nRF52840 | Signal | CON1 pin | TPS43 J1 pin |
| --- | --- | --- | --- | --- | --- |
| D8 | JP1.11 | P1.04 | SDA (I2C data) | 1 | 6 |
| D9 | JP1.12 | P1.06 | SCL (I2C clock) | 2 | 5 |
| VCC | JP2.4 | 3.3 V | VDDHI | 3 | 4 |
| GND | JP1.3, JP1.4, JP2.2 | GND | GND | 4 | 3 |
| D16 | JP2.11 | P0.10 | NRST (trackpad reset) | 5 | 2 |
| D10 | JP2.12 | P0.09 | RDY (interrupt) | 6 | 1 |

The nRF numbers are from ZMK's `arduino_pro_micro_pins.dtsi` and agree with Temper's own
schematic. Earlier revisions of this file had D9, D10 and D16 wrong (P0.09 / P0.11 / P1.06),
which put the I2C clock on the wrong pin and claimed P0.11, which is actually D7, one of
Temper's matrix rows.

**These four pins are confirmed free on Temper.** Its netlist marks D0, D8, D9, D10, D14 and D16
as unconnected. Used: D1 (nice!view CS), D2 (MOSI), D3 (SCK), D4-D7 (rows), D15/D18/D19/D20/D21
(columns).

**CON1 is deliberately the mirror of the trackpad's connector.** The TPS43's own J1 pinout is
`1:RDY 2:NRST 3:GND 4:VDDHI 5:SCL 6:SDA` (Azoteq *ProxSense Standard Trackpad Module* datasheet,
revision 1.06, August 2025), and the FFC cable this board is designed around reverses the
conductor order end to end, so CON1 pin N carries TPS43 pin 7−N. See the cable warning under
[Assembly](#assembly) before you order anything.

Two things worth knowing about that pinout. First, **it changed**: the 2016 revision 1.02 PDF
still mirrored on DigiKey's media server lists TPS43 as `RDY, SDA, GND, VDDHI, SCL, NRST`, and the
revision history records v1.04 (December 2022) as "Update Figure 2-1 and Table 2-1", which is
exactly that table. Always use the copy on azoteq.com. Second, earlier revisions of this project
used a third pinout (`VDD, SDA, SCL, RDY, RST, GND`) that matches neither, and would have put
3.3 V onto RDY and shorted SCL to ground.

Every other Pro Micro pin is a plated through-hole with no copper attached to it: it connects
the nice!nano above to the Temper PCB below and nothing else.

JP1 is the left header row and JP2 the right one, viewed from the **top** of the board with the
nice!nano's USB port pointing away from you, which is the same orientation as looking down at
the nice!nano itself. The board is never flipped during assembly, so the pass-through mapping is
one to one and needs no mirroring.

CON1's two mounting tabs are tied to GND. They are the connector's only mechanical retention,
so they have to be soldered.

## Layout and routing

```
Y +23.50  board top edge
Y +22.15  CON1 courtyard, cable exits straight out over this edge
Y +21.00  CON1 signal pads (0.30 x 1.30 mm on 0.50 mm pitch)
Y +20.30  VCC bus across the top of both pull-ups
Y +20.03  escape lane A   SDA west  /  RDY east      \
Y +19.60  escape lane B   SCL west  /  RST east       >  1.50 mm corridor,
Y +19.18  escape lane C   VCC west  /  GND east      /   0.20 mm tracks
Y +18.00  R1 (SDA pull-up, X -12.00) and R2 (SCL pull-up, X -14.50)
Y +17.75  CON1 mounting tabs, tied together and dropped to the ground plane
Y +12.70  header pin 1
Y -15.24  header pin 12
Y -20.50  board bottom edge
```

The six FFC pads escape south through the corridor between the pad row and the mounting tabs,
three lanes to each side. Each lane holds its own Y until it reaches its own trunk X and then
turns square: a lane that dove diagonally toward its trunk would clip the corner off the lane
below it, and 0.425 mm of lane spacing leaves no room for that.

The lane order is not a choice. The pad nearest the centre has to take the innermost lane so it
can duck under its neighbours' drops, and a lane turning south then blocks every lane below it
from reaching further out. So lane A turns furthest from the centre and lane C nearest to it, and
whichever net lands on lane C is boxed in. Here that is VCC on the west side and GND on the east,
which is convenient: GND only needs to reach the plane, and VCC has to cross the board anyway.

Trunk positions: SDA −9.50, SCL −6.30, VCC −5.00, GND +4.60, RST +5.40, RDY +6.30. SDA runs
*outside* the JP1 pad column rather than in the centre channel, which is what puts the two pull-up
resistors within reach of it.

Six vias, each earning its place:

- **VCC** (2 vias) drops to B.Cu at the corridor exit because lane C cannot travel on F.Cu at
  all, then crosses to JP2.4 and spurs back up to the pull-up bus.
- **SCL** (2 vias) reaches R2 with a B.Cu hop under the SDA trunk and the JP1 pad column.
- **RST** (1 via) hops under the RDY trunk. RDY has the outer trunk, so it must serve the more
  southern header pin or the inner trunk's jog would cut across it. That would otherwise force
  RDY and RST to swap header pins, and this via is what keeps the ZMK overlay untouched.
- **CON1's mounting tabs** (1 via) drop to the ground plane under the connector body, picking up
  the GND escape lane on the way.

B.Cu is otherwise a single 1283 mm2 GND pour with thermal reliefs on the through-hole GND pads,
which also gives the whole I2C run a reference plane underneath. JP1.3, JP1.4 and JP2.2 pick up
GND from the plane, so no ground track has to thread past a header column.

Design rules, all enforced by `build.sh`: 0.20 mm minimum track and clearance, 0.60/0.30 mm
vias, 0.30 mm minimum hole, 0.40 mm copper-to-edge. The tightest feature on the board is the
connector escape: 0.20 mm tracks on 0.40 mm centres. Comfortably inside any cheap 2-layer
process, but it is the number to check if a fab quotes looser capabilities.

## BOM

See `BOM.md` for links and prices.

| Qty | Designator | Part | Footprint |
| --- | --- | --- | --- |
| 2 | JP1, JP2 | 1x12 through-hole positions, 2.54 mm | `PinHeader_1x12_P2.54mm_Vertical` |
| 1 | CON1 | Hirose FH12-6S-0.5SH, 6-pos 0.5 mm FFC, horizontal | `Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal` |
| 2 | R1, R2 | 2.2 kOhm 0805 thick film | `R_0805_2012Metric` |
| 24 | - | **Mill-Max pins** (bottom side, into Temper's sockets) | - |
| 24 | - | **Mill-Max 310 series machine sockets** (top side, for the nice!nano) | - |
| 1 | - | 6-pos 0.5 mm FFC cable, ~50 mm | - |
| 1 | - | Azoteq TPS43-201A-S trackpad module | - |

**Do not use ordinary 2.54 mm breakaway headers here.** Temper is built with Mill-Max 310 series
machine sockets, whose bore takes ~0.5 mm round pins. Standard header pins are 0.64 mm square and
will not fit; forcing them wrecks the socket. The interposer needs Mill-Max pins on the bottom to
plug into Temper, and Mill-Max 310 sockets on top because the nice!nano already has Mill-Max pins
soldered to it. The 1.0 mm holes in this footprint suit both.

CON1 replaces the Molex 503480-0600 called for in earlier revisions. The Molex part's land
pattern was never verified against its datasheet here, and the footprint that shipped with it
used non-plated holes for mounting, which gives a 0.5 mm-pitch connector no solder retention at
all. The Hirose part ships as a datasheet-derived footprint in KiCad's own `Connector_FFC-FPC`
library and has two 1.8 x 2.2 mm SMT solder tabs.

## Assembly

The board is oriented so that the nice!nano ends up on top:

1. **Top side:** solder 24 **Mill-Max 310 machine sockets** at JP1 and JP2. These receive the
   Mill-Max pins already soldered to your nice!nano.
2. **Bottom side:** solder 24 **Mill-Max pins**, pointing down, to plug into Temper's own
   sockets. Not square breakaway header pins, see the BOM note.
3. **Top side:** solder CON1. Both mounting tabs must be soldered; they are the only thing
   holding it on. The cable opening faces the top edge of the board, away from the nice!nano.
4. **Top side:** solder R1 and R2.
5. Unplug the nice!nano from Temper, plug the interposer into Temper's sockets, then plug the
   nice!nano into the interposer.
6. Connect the TPS43 with the FFC cable. It runs straight out over the top edge toward the
   thumb cluster, with no fold, and never passes under the nice!nano.

### Verify the cable before you fab this board

CON1 is wired for a cable that **reverses** the conductor order, so that CON1 pin N reaches
TPS43 J1 pin 7−N. If your cable is straight-through instead, this board is wrong and every signal
is scrambled: 3.3 V would land on the trackpad's RDY pin.

Do not trust the "Type A" / "Type B" label. The naming is not standardised. DigiKey and Molex
call same-side contacts Type A and opposite-side Type D; other vendors call the same thing Type B,
Type 1 or Type 2. FH12-6S-0.5SH is bottom-contact, so at the interposer end the conductors face
down toward the board, but that alone does not tell you the mapping.

**Check it with a meter.** Lay the cable out as it will actually run between the two boards, then
ring out conductor 1 at one end against each conductor at the other:

- continuity from end-A conductor 1 to end-B conductor **6** confirms reversed: this board is
  correct as fabbed
- continuity from end-A conductor 1 to end-B conductor **1** means straight-through: **do not
  fab this board**, see below

CON1's pinout is derived in `gen_schematic.py` from `TPS43_J1` (the datasheet table) and
`CON1_MIRRORED` (the cable's mapping), so the relationship is explicit rather than a magic
constant. Setting `CON1_MIRRORED = False` produces the correct *netlist* for a straight-through
cable, but it is not a drop-in change and the generator will refuse to route it: flipping the
cable flips the escape-lane order, which moves the pull-ups to the east side and swaps which
header column carries I2C, so the ZMK overlay changes too. `route()`, the trunk constants and the
resistor placement have to be redone together. The assertion tells you exactly that if you try.

**Check the USB-C clearance before ordering.** CON1 spans Y +14.25 to +22.15, directly in front
of the nice!nano's USB-C port. Mill-Max sockets lift the module only ~2 mm and the FH12 is about
2 mm tall, so this is tighter than it would be with tall sockets. Measure it.

**Temper's battery pads sit under the nice!nano** (BT1, X 173.62..182.83, Y 57.82..63.08), and
the assembly guide has you solder battery wires there. The interposer's B.Cu ground pour will end
up directly over that wiring with only the socket standoff in between. Dress the wires flat and
check for chafing before seating the interposer.

## Ordering the PCB

Upload `output/temper-tps43-interposer-gerbers.zip`, or the `.kicad_pcb` directly if the fab
accepts it.

- Layers: 2
- Thickness: 1.0 mm
- Surface finish: **ENIG** (recommended: the 0.5 mm FFC pads are fine pitch)
- Copper weight: 1 oz
- Minimum track / clearance required: 0.20 mm / 0.20 mm
- Minimum drill: 0.30 mm

## ZMK firmware

The pin assignment above is exactly what the original design specified, so the overlay is
unchanged.

### `config/temper_right.conf`

```
CONFIG_INPUT_TPS43=y
CONFIG_I2C=y
CONFIG_ZMK_POINTING=y
CONFIG_NFCT_PINS_AS_GPIOS=y
```

`CONFIG_NFCT_PINS_AS_GPIOS=y` is **required**, not optional. RDY lands on D10 = P0.09 and the
trackpad reset on D16 = P0.10, and those two are the nRF52840's NFC antenna pins. Without this
they are not GPIOs and neither signal works.

### `config/temper_right.overlay`

```dts
#include "temper.dtsi"

&default_transform {
    col-offset = <5>;
};

&kscan0 {
    col-gpios
        = <&pro_micro 15 GPIO_ACTIVE_HIGH>
        , <&pro_micro 18 GPIO_ACTIVE_HIGH>
        , <&pro_micro 19 GPIO_ACTIVE_HIGH>
        , <&pro_micro 20 GPIO_ACTIVE_HIGH>
        , <&pro_micro 21 GPIO_ACTIVE_HIGH>
        ;
};

/* I2C on D8(SDA) / D9(SCL), a separate bus from the nice!view SPI on D1/D2/D3.
 * D8 = P1.04 and D9 = P1.06. Earlier revisions of this file said D9 = P0.09, which is
 * wrong: P0.09 is D10. Verified against ZMK's arduino_pro_micro_pins.dtsi and against
 * Temper's own schematic symbol pin names. */
&pinctrl {
    i2c1_default: i2c1_default {
        group1 {
            psels = <NRF_PSEL(TWIM_SDA, 1, 4)>,
                    <NRF_PSEL(TWIM_SCL, 1, 6)>;
        };
    };
    i2c1_sleep: i2c1_sleep {
        group1 {
            psels = <NRF_PSEL(TWIM_SDA, 1, 4)>,
                    <NRF_PSEL(TWIM_SCL, 1, 6)>;
            low-power-enable;
        };
    };
};

&i2c1 {
    compatible = "nordic,nrf-twim";
    status = "okay";
    clock-frequency = <I2C_BITRATE_FAST>;
    pinctrl-0 = <&i2c1_default>;
    pinctrl-1 = <&i2c1_sleep>;
    pinctrl-names = "default", "sleep";

    tps43: trackpad@74 {
        compatible = "azoteq,tps43";
        reg = <0x74>;
        rdy-gpios = <&pro_micro 10 GPIO_ACTIVE_HIGH>;
        rst-gpios = <&pro_micro 16 GPIO_ACTIVE_HIGH>;
        enable-power-management;
        scroll;
        two-finger-tap;
        single-tap;
        press-and-hold;
    };
};

/ {
    split_inputs {
        #address-cells = <1>;
        #size-cells = <0>;
        tps43_split: tps43_split@0 {
            compatible = "zmk,input-split";
            reg = <0>;
            device = <&tps43>;
        };
    };
};
```

The `rdy-gpios` and `rst-gpios` numbers go through the `pro_micro` nexus, so they are correct as
written regardless of the nRF pin numbering.

### Central (left) side

```dts
/ {
    split_inputs {
        #address-cells = <1>;
        #size-cells = <0>;
        tps43_split: tps43_split@0 {
            compatible = "zmk,input-split";
            reg = <0>;
        };
    };
    tps43_listener: tps43_listener {
        compatible = "zmk,input-listener";
        device = <&tps43_split>;
        status = "okay";
    };
};
```

### Build workflow

Add `stelmakhdigital/zmk_driver_azoteq` as an external module in the GitHub Actions build
workflow's `modules` matrix variable.
